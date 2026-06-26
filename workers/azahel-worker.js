/**
 * Azahel Nemotrin - Cloudflare Workers Edge Function
 * Recibe datos del celular, valida, almacena y responde
 * Deploy: wrangler deploy
 */

const API_VERSION = "v1";
const MAX_PAYLOAD_SIZE = 1024 * 1024; // 1MB

interface DataPayload {
  data: Record<string, any>;
  timestamp: string;
  signature: string;
}

interface ProcessResponse {
  status: "success" | "error";
  id?: string;
  timestamp?: string;
  hash?: string;
  message?: string;
  error?: string;
}

/**
 * Valida la integridad del payload
 */
function validateSignature(payload: DataPayload, contentBody: string): boolean {
  // En producción, implementar verificación HMAC
  // Por ahora, validar que signature existe
  return payload.signature && payload.signature.length === 64; // SHA256
}

/**
 * Genera ID único para la transacción
 */
function generateTransactionId(): string {
  return `txn-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Calcula hash SHA256 del payload
 */
async function calculateSha256(data: string): Promise<string> {
  const encoder = new TextEncoder();
  const dataBuffer = encoder.encode(data);
  const hashBuffer = await crypto.subtle.digest("SHA-256", dataBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
}

/**
 * Handler POST /api/v1/process
 */
export default {
  async fetch(
    request: Request,
    env: Env,
    ctx: ExecutionContext
  ): Promise<Response> {
    // CORS preflight
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type, X-Client-Version, X-Signature",
        },
      });
    }

    // Solo aceptar POST
    if (request.method !== "POST") {
      return new Response(JSON.stringify({ error: "Method not allowed" }), {
        status: 405,
        headers: { "Content-Type": "application/json" },
      });
    }

    try {
      // Parsear request
      const contentType = request.headers.get("Content-Type");
      if (!contentType?.includes("application/json")) {
        return new Response(
          JSON.stringify({ error: "Content-Type must be application/json" }),
          { status: 400, headers: { "Content-Type": "application/json" } }
        );
      }

      const body = await request.text();

      // Validar tamaño
      if (body.length > MAX_PAYLOAD_SIZE) {
        return new Response(
          JSON.stringify({ error: "Payload too large" }),
          { status: 413, headers: { "Content-Type": "application/json" } }
        );
      }

      // Parsear JSON
      let payload: DataPayload;
      try {
        payload = JSON.parse(body);
      } catch (e) {
        return new Response(
          JSON.stringify({ error: "Invalid JSON" }),
          { status: 400, headers: { "Content-Type": "application/json" } }
        );
      }

      // Validar estructura
      if (!payload.data || !payload.timestamp || !payload.signature) {
        return new Response(
          JSON.stringify({
            error: "Missing required fields: data, timestamp, signature",
          }),
          { status: 400, headers: { "Content-Type": "application/json" } }
        );
      }

      // Validar firma
      if (!validateSignature(payload, body)) {
        return new Response(
          JSON.stringify({ error: "Invalid signature" }),
          { status: 401, headers: { "Content-Type": "application/json" } }
        );
      }

      // Generar ID y hash
      const txnId = generateTransactionId();
      const payloadHash = await calculateSha256(body);

      // Almacenar en KV Store (si está configurado)
      if (env.AZAHEL_KV) {
        const kvData = {
          id: txnId,
          payload: payload,
          hash: payloadHash,
          received_at: new Date().toISOString(),
        };
        await env.AZAHEL_KV.put(txnId, JSON.stringify(kvData), {
          expirationTtl: 86400 * 30, // 30 días
        });
      }

      // Loguear en Analytics Engine (si está disponible)
      if (env.AZAHEL_ANALYTICS) {
        ctx.waitUntil(
          env.AZAHEL_ANALYTICS.writeDataPoint({
            indexes: [txnId],
            blobs: [
              JSON.stringify({
                type: "process",
                gflops: payload.data.gflops,
                device: payload.data.device,
              }),
            ],
          })
        );
      }

      // Respuesta exitosa
      const response: ProcessResponse = {
        status: "success",
        id: txnId,
        timestamp: new Date().toISOString(),
        hash: payloadHash,
        message: `Datos recibidos y procesados en edge. Vigilante #201 confirma.`,
      };

      return new Response(JSON.stringify(response), {
        status: 200,
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
          "X-Transaction-ID": txnId,
          "X-Payload-Hash": payloadHash,
        },
      });
    } catch (error) {
      console.error("Error processing request:", error);

      const response: ProcessResponse = {
        status: "error",
        error: error instanceof Error ? error.message : "Unknown error",
      };

      return new Response(JSON.stringify(response), {
        status: 500,
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
      });
    }
  },
};

interface Env {
  AZAHEL_KV?: KVNamespace;
  AZAHEL_ANALYTICS?: AnalyticsEngineDatapoint;
}

interface AnalyticsEngineDatapoint {
  writeDataPoint(data: any): Promise<void>;
}

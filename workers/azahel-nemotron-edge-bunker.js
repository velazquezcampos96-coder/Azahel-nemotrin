/**
 * AZAHEL NEMOTRON - BÚNKER DE BORDE KPKAVE v2.5
 * 
 * Edge Function en Cloudflare que recibe cálculos del celular,
 * valida integridad, genera transacciones únicas y almacena resultados.
 * 
 * Deploy: wrangler deploy
 * Route: https://tu-dominio.com/api/v1/process
 */

const API_VERSION = "v2.5";
const MAX_PAYLOAD_SIZE = 5 * 1024 * 1024; // 5MB

/**
 * Valida estructura del payload KPKAVE
 * Requiere: gflops, tiempo_procesamiento, dispositivo
 */
function validatePayloadContract(payload) {
  const required = ["gflops", "tiempo_procesamiento", "dispositivo"];
  
  for (const field of required) {
    if (!(field in payload)) {
      return {
        valid: false,
        error: `Campo requerido faltante: ${field}`
      };
    }
  }
  
  // Validar tipos
  if (typeof payload.gflops !== "number" || payload.gflops <= 0) {
    return { valid: false, error: "gflops debe ser número positivo" };
  }
  
  if (typeof payload.tiempo_procesamiento !== "number" || payload.tiempo_procesamiento <= 0) {
    return { valid: false, error: "tiempo_procesamiento debe ser número positivo" };
  }
  
  if (typeof payload.dispositivo !== "string" || payload.dispositivo.length === 0) {
    return { valid: false, error: "dispositivo debe ser string no vacío" };
  }
  
  return { valid: true };
}

/**
 * Genera Transaction ID único para auditoría
 */
function generateTransactionId() {
  const timestamp = Date.now();
  const randomSuffix = Math.random().toString(36).substr(2, 9).toUpperCase();
  const nonce = Math.floor(Math.random() * 10000).toString().padStart(4, "0");
  return `TXN-${timestamp}-${randomSuffix}-${nonce}`;
}

/**
 * Calcula hash SHA256 del payload para integridad
 */
async function calculatePayloadHash(data) {
  const encoder = new TextEncoder();
  const dataBuffer = encoder.encode(JSON.stringify(data));
  const hashBuffer = await crypto.subtle.digest("SHA-256", dataBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, "0")).join("");
}

/**
 * Enriquece metadata del procesamiento con información del edge
 */
function enrichMetadata(payload, transactionId, timestamp, cfData) {
  return {
    // Datos del procesamiento local
    gflops: payload.gflops,
    tiempo_procesamiento: payload.tiempo_procesamiento,
    dispositivo: payload.dispositivo,
    
    // Metadata adicional del payload
    ...payload,
    
    // Metadata transaccional
    transactionId: transactionId,
    status: "SUCCESS",
    fechaRecepcion: new Date(timestamp).toISOString(),
    timestamp: timestamp,
    
    // Información del edge
    cloudflare: {
      version: API_VERSION,
      colo: cfData?.colo || "unknown",
      country: cfData?.country || "unknown",
      continent: cfData?.continent || "unknown",
      asn: cfData?.asn || "unknown"
    }
  };
}

/**
 * Handler principal del Worker
 */
export default {
  async fetch(request, env, ctx) {
    const requestId = crypto.getRandomValues(new Uint8Array(8));
    const requestIdHex = Array.from(requestId).map(b => b.toString(16).padStart(2, "0")).join("");
    
    console.log(`[${requestIdHex}] AZAHEL NEMOTRON v${API_VERSION} - Solicitud recibida`);
    
    // ===== 1. ESCUDO CORS: Validar método HTTP =====
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type, X-Client-Version",
          "Access-Control-Max-Age": "3600"
        }
      });
    }
    
    if (request.method !== "POST") {
      console.log(`[${requestIdHex}] ❌ Método no permitido: ${request.method}`);
      return new Response(JSON.stringify({
        error: "Método no permitido, perro.",
        detalle: "Solo aceptamos POST en este endpoint",
        metodo_recibido: request.method
      }), {
        status: 405,
        headers: {
          "Content-Type": "application/json",
          "X-Request-ID": requestIdHex
        }
      });
    }
    
    try {
      // ===== 2. VALIDACIÓN DE CONTENT-TYPE =====
      const contentType = request.headers.get("Content-Type");
      if (!contentType?.includes("application/json")) {
        console.log(`[${requestIdHex}] ❌ Content-Type inválido: ${contentType}`);
        return new Response(JSON.stringify({
          error: "Content-Type inválido",
          esperado: "application/json",
          recibido: contentType
        }), {
          status: 415,
          headers: {
            "Content-Type": "application/json",
            "X-Request-ID": requestIdHex
          }
        });
      }
      
      // ===== 3. LECTURA Y VALIDACIÓN DE TAMAÑO =====
      const bodyText = await request.text();
      
      if (bodyText.length > MAX_PAYLOAD_SIZE) {
        console.log(`[${requestIdHex}] ❌ Payload demasiado grande: ${bodyText.length} bytes`);
        return new Response(JSON.stringify({
          error: "Payload demasiado grande",
          limite: `${MAX_PAYLOAD_SIZE} bytes`,
          recibido: `${bodyText.length} bytes`
        }), {
          status: 413,
          headers: {
            "Content-Type": "application/json",
            "X-Request-ID": requestIdHex
          }
        });
      }
      
      // ===== 4. PARSEO JSON =====
      let payload;
      try {
        payload = JSON.parse(bodyText);
      } catch (jsonErr) {
        console.log(`[${requestIdHex}] ❌ JSON inválido: ${jsonErr.message}`);
        return new Response(JSON.stringify({
          error: "Payload corrupto o incompleto.",
          detalle: "JSON inválido",
          mensaje_error: jsonErr.message
        }), {
          status: 400,
          headers: {
            "Content-Type": "application/json",
            "X-Request-ID": requestIdHex
          }
        });
      }
      
      // ===== 5. VALIDACIÓN QUIRÚRGICA DEL CONTRATO =====
      const validation = validatePayloadContract(payload);
      if (!validation.valid) {
        console.log(`[${requestIdHex}] ❌ Validación fallida: ${validation.error}`);
        return new Response(JSON.stringify({
          error: "Payload corrupto o incompleto.",
          detalle: validation.error,
          campos_requeridos: ["gflops", "tiempo_procesamiento", "dispositivo"],
          campos_recibidos: Object.keys(payload)
        }), {
          status: 400,
          headers: {
            "Content-Type": "application/json",
            "X-Request-ID": requestIdHex
          }
        });
      }
      
      // ===== 6. GENERACIÓN DE IDENTIDAD TRANSACCIONAL =====
      const timestamp = Date.now();
      const transactionId = generateTransactionId();
      const payloadHash = await calculatePayloadHash(payload);
      
      console.log(`[${requestIdHex}] ✓ Validación exitosa - TXN: ${transactionId}`);
      
      // ===== 7. ENRIQUECIMIENTO DE METADATA =====
      const cfData = request.cf || {};
      const metadataProcesamiento = enrichMetadata(
        payload,
        transactionId,
        timestamp,
        cfData
      );
      
      // ===== 8. PERSISTENCIA EN KV STORE =====
      if (env.RENDIMIENTO_KV) {
        try {
          await env.RENDIMIENTO_KV.put(
            transactionId,
            JSON.stringify(metadataProcesamiento),
            {
              expirationTtl: 86400 * 90, // 90 días
              metadata: {
                gflops: payload.gflops,
                dispositivo: payload.dispositivo,
                creado: new Date(timestamp).toISOString()
              }
            }
          );
          console.log(`[${requestIdHex}] ✓ Persistido en KV Store`)
        } catch (kvErr) {
          console.warn(`[${requestIdHex}] ⚠ Fallo al escribir KV: ${kvErr.message}`);
          // No fallar la respuesta por error en KV
        }
      } else {
        console.warn(`[${requestIdHex}] ⚠ RENDIMIENTO_KV no vinculado - metadata en memoria solamente`);
      }
      
      // ===== 9. LOGGING EN ANALYTICS ENGINE (opcional) =====
      if (env.AZAHEL_ANALYTICS) {
        try {
          ctx.waitUntil(
            env.AZAHEL_ANALYTICS.writeDataPoint({
              indexes: [transactionId, payload.dispositivo],
              blobs: [
                JSON.stringify({
                  type: "pytorch_process",
                  gflops: payload.gflops,
                  tiempo: payload.tiempo_procesamiento,
                  dispositivo: payload.dispositivo,
                  pais: cfData.country,
                  timestamp: timestamp
                })
              ]
            })
          );
          console.log(`[${requestIdHex}] ✓ Logged to Analytics Engine`);
        } catch (analyticsErr) {
          console.warn(`[${requestIdHex}] ⚠ Analytics error: ${analyticsErr.message}`);
        }
      }
      
      // ===== 10. RESPUESTA LIMPIA AL CLIENTE =====
      const responsePayload = {
        mensaje: "PIPELINE COMPLETADO EN EL BORDE",
        validado: true,
        meta: {
          transactionId: transactionId,
          status: "SUCCESS",
          gflops: payload.gflops,
          tiempo: payload.tiempo_procesamiento,
          nodo: payload.dispositivo,
          fecha: new Date(timestamp).toISOString(),
          payloadHash: payloadHash,
          cloudflare: {
            version: API_VERSION,
            pais: cfData.country,
            colo: cfData.colo
          }
        }
      };
      
      console.log(`[${requestIdHex}] ✓ Respuesta enviada - TXN: ${transactionId}`);
      
      return new Response(JSON.stringify(responsePayload), {
        status: 200,
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
          "X-Transaction-ID": transactionId,
          "X-Payload-Hash": payloadHash,
          "X-Request-ID": requestIdHex,
          "X-Version": API_VERSION,
          "Cache-Control": "no-cache, no-store, must-revalidate"
        }
      });
      
    } catch (err) {
      console.error(`[${requestIdHex}] ❌ ERROR CRÍTICO: ${err.message}`, err);
      
      return new Response(JSON.stringify({
        error: "Fallo crítico en el Edge: " + err.message,
        detalle: "Contacta a los Vigilantes del KpKave",
        requestId: requestIdHex,
        timestamp: new Date().toISOString()
      }), {
        status: 500,
        headers: {
          "Content-Type": "application/json",
          "X-Request-ID": requestIdHex,
          "X-Version": API_VERSION
        }
      });
    }
  }
};

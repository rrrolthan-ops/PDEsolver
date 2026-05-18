import { useRef, useState } from "react";
import { extractFromImage } from "../api/client";
import type { VisionExtractionResult } from "../api/types";

interface Props {
  onExtracted: (result: VisionExtractionResult) => void;
}

const ACCEPT = "image/jpeg,image/png,image/webp,image/heic,image/gif";

/**
 * Image upload panel.
 *
 * Three input paths:
 * 1. File picker (button).
 * 2. Drag & drop on the panel.
 * 3. Native camera capture on mobile via `capture="environment"`.
 *
 * On submit we POST a multipart upload to /vision/extract, and on
 * success we pass the result up to the parent which routes to the
 * confirmation panel.
 */
export function ImageUpload({ onExtracted }: Props) {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const cameraInputRef = useRef<HTMLInputElement | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [hint, setHint] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);

  const acceptFile = (f: File) => {
    setFile(f);
    setError(null);
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(URL.createObjectURL(f));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) acceptFile(f);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files?.[0];
    if (f) acceptFile(f);
  };

  const handleSubmit = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const result = await extractFromImage(file, hint || undefined);
      onExtracted(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="panel">
      <h2>Subir foto del problema</h2>
      <p style={{ marginTop: 0, color: "var(--text-muted)", fontSize: 14 }}>
        Sube una foto de una página de libro, examen, pizarra o apunte. La
        imagen se procesa con Claude (modelo claude-haiku-4-5) que
        transcribe la fórmula y la estructura como{" "}
        <code style={{ fontSize: 12 }}>PDEProblem</code>. Tú confirmas la
        interpretación antes de resolver.
      </p>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        style={{
          border: `2px dashed ${dragOver ? "var(--accent)" : "var(--border)"}`,
          borderRadius: 10,
          padding: previewUrl ? 12 : 36,
          textAlign: "center",
          marginBottom: 12,
          transition: "border-color 0.15s",
          background: dragOver ? "var(--accent-soft)" : "transparent",
        }}
      >
        {previewUrl ? (
          <img
            src={previewUrl}
            alt="Previsualización"
            style={{
              maxWidth: "100%",
              maxHeight: 280,
              borderRadius: 6,
              display: "block",
              margin: "0 auto",
            }}
          />
        ) : (
          <div style={{ color: "var(--text-muted)" }}>
            <p style={{ margin: 0, fontSize: 15 }}>
              Arrastra una imagen aquí
            </p>
            <p style={{ margin: "4px 0 0", fontSize: 13 }}>
              o usa los botones de abajo
            </p>
          </div>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept={ACCEPT}
        onChange={handleFileChange}
        style={{ display: "none" }}
      />
      <input
        ref={cameraInputRef}
        type="file"
        accept="image/*"
        // Mobile-only: prompt the camera UI directly.
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        {...({ capture: "environment" } as any)}
        onChange={handleFileChange}
        style={{ display: "none" }}
      />

      <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        <button
          type="button"
          className="solve-button"
          style={{
            background: "transparent",
            color: "var(--accent)",
            border: "1px solid var(--accent)",
          }}
          onClick={() => fileInputRef.current?.click()}
        >
          Elegir archivo
        </button>
        <button
          type="button"
          className="solve-button"
          style={{
            background: "transparent",
            color: "var(--accent)",
            border: "1px solid var(--accent)",
          }}
          onClick={() => cameraInputRef.current?.click()}
        >
          Tomar foto
        </button>
        {file && (
          <button
            type="button"
            className="solve-button"
            style={{
              background: "transparent",
              color: "var(--text-muted)",
              border: "1px solid var(--border)",
            }}
            onClick={() => {
              setFile(null);
              if (previewUrl) URL.revokeObjectURL(previewUrl);
              setPreviewUrl(null);
            }}
          >
            Quitar
          </button>
        )}
      </div>

      <label className="field">
        <span className="field-label">
          Contexto opcional (lo que ya sabes del problema)
        </span>
        <textarea
          value={hint}
          onChange={(e) => setHint(e.target.value)}
          rows={2}
          placeholder="Ej: es la ecuación del calor en una barra"
          spellCheck={false}
        />
      </label>

      <button
        type="button"
        className="solve-button"
        onClick={handleSubmit}
        disabled={!file || loading}
      >
        {loading ? "Procesando imagen…" : "Procesar y revisar"}
      </button>

      {error && (
        <div className="error-banner" role="alert" style={{ marginTop: 12 }}>
          <strong>No pude procesar la imagen:</strong> {error}
        </div>
      )}

      <p style={{ marginTop: 12, fontSize: 12, color: "var(--text-muted)" }}>
        El modelo de visión <strong>sólo transcribe y estructura</strong>; no
        resuelve. La resolución matemática siempre la hace el motor
        simbólico determinista. Verás la imagen original junto a la
        transcripción para que confirmes antes de pasar al solver.
      </p>
    </section>
  );
}

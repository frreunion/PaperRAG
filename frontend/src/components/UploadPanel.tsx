import { Upload } from "lucide-react";
import { useState } from "react";

type Props = {
  onUpload: (file: File) => Promise<void>;
};

export function UploadPanel({ onUpload }: Props) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function handleFile(file: File | undefined) {
    if (!file) return;
    setBusy(true);
    setError("");
    try {
      await onUpload(file);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "上传失败");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel upload-panel">
      <div>
        <h2>上传论文</h2>
        <p>支持文本型 PDF，上传后自动解析、切块并建立索引。</p>
      </div>
      <label className="upload-button">
        <Upload size={18} />
        <span>{busy ? "处理中..." : "选择 PDF"}</span>
        <input
          type="file"
          accept="application/pdf,.pdf"
          disabled={busy}
          onChange={(event) => void handleFile(event.target.files?.[0])}
        />
      </label>
      {error ? <p className="error">{error}</p> : null}
    </section>
  );
}

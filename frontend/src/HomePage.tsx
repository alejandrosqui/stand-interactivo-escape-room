import { FormEvent, useState } from "react";

export function HomePage() {
  const [codigo, setCodigo] = useState("");

  const ingresar = (evento: FormEvent) => {
    evento.preventDefault();
    if (codigo.trim()) {
      window.location.href = `/experiencia/${codigo.trim().toUpperCase()}`;
    }
  };

  return (
    <main className="landing-shell">
      <nav>
        <span className="brand-mark">◈</span>
        <span>STAND//ESCAPE</span>
        <a href="/admin">Administrar</a>
      </nav>
      <section className="landing-copy">
        <span className="eyebrow">DESAFÍO INTERACTIVO · 3–7 MINUTOS</span>
        <h1>El stand esconde<br /><em>una misión.</em></h1>
        <p>
          Explorá el espacio, encontrá las pistas y resolvé el código antes de
          que se termine el tiempo.
        </p>
        <form className="code-form" onSubmit={ingresar}>
          <input
            value={codigo}
            onChange={(e) => setCodigo(e.target.value)}
            placeholder="CÓDIGO DE MISIÓN"
            aria-label="Código de misión"
          />
          <button className="primary-button">Ingresar</button>
        </form>
        <small>También podés escanear el QR disponible en el stand.</small>
      </section>
      <div className="orb" />
    </main>
  );
}


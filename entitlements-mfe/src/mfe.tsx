import { StrictMode } from "react";
import { createRoot, type Root } from "react-dom/client";

import { App } from "./App";
import styles from "./styles.css?inline";

class SspEntitlementsElement extends HTMLElement {
  private root: Root | null = null;

  connectedCallback(): void {
    const shadow = this.shadowRoot ?? this.attachShadow({ mode: "open" });
    const style = document.createElement("style");
    style.textContent = styles;
    const mount = document.createElement("div");
    shadow.replaceChildren(style, mount);
    this.root = createRoot(mount);
    this.root.render(
      <StrictMode>
        <App apiBase={this.getAttribute("api-base") ?? import.meta.env.VITE_API_BASE ?? ""} />
      </StrictMode>,
    );
  }

  disconnectedCallback(): void {
    this.root?.unmount();
    this.root = null;
  }
}

if (!customElements.get("ssp-entitlements")) {
  customElements.define("ssp-entitlements", SspEntitlementsElement);
}

export { SspEntitlementsElement };

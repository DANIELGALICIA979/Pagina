// Fade inicial del texto y control del botón y scroll
window.addEventListener("load", () => {
  const titulo = document.querySelector(".hero h1");
  const boton = document.getElementById("conocenosBtn");
  const seccionExtra = document.querySelector(".extra");

  // Mostrar el título con tu animación original
  if (titulo) titulo.classList.add("show");

  // Bloquear scroll al inicio
  document.body.classList.add("no-scroll");

  // Añadir la clase 'active' al botón en el siguiente frame para que la animación se inicialice de forma inmediata y suave
  // (evita hacer style.opacity = "1", que provocaba "aparecer súbito")
  requestAnimationFrame(() => {
    // pequeña micro-pausa para forzar el layout antes de activar la animación
    setTimeout(() => {
      boton.classList.add("active");
    }, 50);
  });

  // Manejo del click / enter / espacio del botón
  const activarScrollAbajo = () => {
    // permitir temporalmente el scroll para que scrollIntoView funcione
    document.body.classList.remove("no-scroll");
    seccionExtra.scrollIntoView({ behavior: "smooth" });

    // Usamos un IntersectionObserver para saber cuándo la sección está visible
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && entry.intersectionRatio > 0.7) {
          // La sección inferior está mayormente visible: activamos bloqueo de scroll hacia arriba
          enableBlockScrollUp();
          observer.disconnect();
        }
      });
    }, { threshold: [0.7] });

    observer.observe(seccionExtra);
  };

  boton.addEventListener("click", activarScrollAbajo);
  // soporte accesible: activar con teclado
  boton.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " " || e.key === "Spacebar") {
      e.preventDefault();
      activarScrollAbajo();
    }
  });

  // ---------------------------
  // Bloqueo de scroll hacia arriba (después de llegar a la sección)
  // ---------------------------
  function enableBlockScrollUp() {
    // PRECAUCIÓN: añadimos listeners con passive:false cuando sea necesario para poder preventDefault
    const onWheel = (e) => {
      // deltaY < 0 => intento de subir (wheel hacia arriba)
      if (e.deltaY < 0) {
        e.preventDefault();
      }
      // Si el usuario hace scroll hacia abajo, permitimos.
    };

    let touchStartY = null;
    const onTouchStart = (e) => {
      if (e.touches && e.touches.length) touchStartY = e.touches[0].clientY;
    };
    const onTouchMove = (e) => {
      if (!touchStartY) return;
      const currentY = e.touches[0].clientY;
      const diff = currentY - touchStartY; // positivo = move down (pulling down = wanting to go up)
      if (diff > 0) {
        // intento de desplazar hacia abajo el dedo (lo que provocaría scroll hacia arriba)
        e.preventDefault();
      }
    };

    const onKeyDown = (e) => {
      const keysBlock = ["ArrowUp", "PageUp", "Home"];
      if (keysBlock.includes(e.key)) {
        e.preventDefault();
      }
    };

    // También, en caso de que el usuario intente setear scroll por JS/manual, forzamos la posición mínima:
    const onScroll = () => {
      const minY = seccionExtra.offsetTop;
      if (window.scrollY < minY) {
        window.scrollTo({ top: minY });
      }
    };

    // Añadimos listeners con las opciones necesarias:
    window.addEventListener("wheel", onWheel, { passive: false });
    window.addEventListener("touchstart", onTouchStart, { passive: false });
    window.addEventListener("touchmove", onTouchMove, { passive: false });
    window.addEventListener("keydown", onKeyDown, { passive: false });
    window.addEventListener("scroll", onScroll, { passive: true });

    // Si quieres quitar por completo barras de scroll, podrías usar overflow hidden; aquí NO lo forzamos,
    // porque queremos permitir scroll hacia abajo si la sección lo requiere.
    // guardamos referencias en window para poder removerlos si se necesitara:
    window._blockers = { onWheel, onTouchStart, onTouchMove, onKeyDown, onScroll };
  }

  // (opcional) función pública para desactivar el bloqueo si más tarde quieres permitir volver arriba
  window.disableBlockScrollUp = function() {
    if (window._blockers) {
      window.removeEventListener("wheel", window._blockers.onWheel);
      window.removeEventListener("touchstart", window._blockers.onTouchStart);
      window.removeEventListener("touchmove", window._blockers.onTouchMove);
      window.removeEventListener("keydown", window._blockers.onKeyDown);
      window.removeEventListener("scroll", window._blockers.onScroll);
      window._blockers = null;
    }
  };
});


// === Animaciones de la sección EXTRA ===
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add("visible");

      // Si es una columna (fade-seq), aplicamos delay progresivo
      if (entry.target.classList.contains("fade-seq")) {
        const siblings = Array.from(document.querySelectorAll(".fade-seq"));
        const index = siblings.indexOf(entry.target);
        entry.target.style.transitionDelay = `${index * 0.3}s`;
      }

      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.3 });

document.querySelectorAll(".fade-in-left, .fade-in-right, .fade-seq")
  .forEach(el => observer.observe(el));

  
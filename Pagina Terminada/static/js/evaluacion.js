document.getElementById('form-evaluacion').addEventListener('submit', function (e) {
  e.preventDefault(); // evita recargar la página

  let puntuacion = 0;

  const edad = parseInt(document.getElementById('edad').value) || 0;
  const empleo = document.getElementById('empleo').value;
  const dependientes = document.getElementById('dependientes').value;
  const otrosApoyos = document.getElementById('otros-apoyos').value;
  const discapacidad = document.getElementById('discapacidad').value;

  // Asignar puntos según las respuestas
  if (edad < 18 || edad > 65) puntuacion += 10;  // personas vulnerables
  if (empleo === 'no') puntuacion += 15;
  if (dependientes === '1') puntuacion += 5;
  else if (dependientes === '3') puntuacion += 10;
  if (otrosApoyos === 'no') puntuacion += 5;
  if (discapacidad === 'si') puntuacion += 10;

  // Determinar nivel de apoyo
  let nivel = '';
  if (puntuacion >= 35) nivel = 'Apoyo Alto';
  else if (puntuacion >= 20) nivel = 'Apoyo Medio';
  else if (puntuacion >= 10) nivel = 'Apoyo Básico';
  else nivel = 'No elegible';

  // Mostrar resultado en modal
  const modal = document.getElementById('modal-resultado');
  const modalPuntuacion = document.getElementById('modal-puntuacion');
  const modalNivel = document.getElementById('modal-nivel');
  modalPuntuacion.textContent = puntuacion;
  modalNivel.textContent = nivel;
  modal.classList.remove('oculto');
  document.body.classList.add('no-scroll');
});

// Cerrar modal
document.addEventListener('click', function (e) {
  const modal = document.getElementById('modal-resultado');
  if (!modal) return;
  // cerrar si se pulsa el botón de cerrar
  if (e.target.matches('.modal-close')) {
    modal.classList.add('oculto');
    document.body.classList.remove('no-scroll');
  }
  // cerrar si se pulsa fuera del contenido (overlay)
  if (e.target === modal) {
    modal.classList.add('oculto');
    document.body.classList.remove('no-scroll');
  }
});



document.getElementById('contactForm').addEventListener('submit', function(event) {

    const nombre = document.getElementById('nombre').value.trim();
    const apellido = document.getElementById('apellido').value.trim();
    const correo = document.getElementById('correo').value.trim();
    const mensaje = document.getElementById('mensaje').value.trim();
    const suscripcion = document.getElementById('suscripcion').checked;


    if (nombre === '' || apellido === '' || correo === '' || mensaje === '') {
        alert('Por favor, completa todos los campos requeridos.');
        event.preventDefault();
    }

    const correoRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!correoRegex.test(correo)) {
        alert('Por favor, ingresa una dirección de correo electrónico válida.');
        event.preventDefault();
        return;
    }


    if (suscripcion) {
        alert('Gracias por suscribirte!');
    }
});

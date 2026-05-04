document.getElementById("btn-signin").addEventListener("click", login);
 
function login() {
    const btn = document.getElementById("btn-signin");
    const email = document.getElementById("user-email").value;
    const password = document.getElementById("user-password").value;
 
    if (email === "") {
        Swal.fire({
            title: 'Correo electrónico no ingresado',
            text: 'Debe ingresar su correo electrónico.',
            icon: 'warning',
            confirmButtonText: 'Aceptar'
        });
        return;
    }
 
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        Swal.fire({
            title: 'Correo inválido',
            text: 'Ingrese un correo electrónico válido.',
            icon: 'warning',
            confirmButtonText: 'Aceptar'
        });
        return;
    }
 
    if (password === "") {
        Swal.fire({
            title: 'Contraseña no ingresada',
            text: 'Debe ingresar una contraseña.',
            icon: 'warning',
            confirmButtonText: 'Aceptar'
        });
        return;
    }
 
    const data = {
        email: email,
        password: password
    };
 
    btn.disabled = true;
 
    fetch('/api/login', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            window.location.href = "/welcome";
        } else {
            Swal.fire({
                title: 'No se pudo iniciar sesión',
                text: result.message,
                icon: 'error',
                confirmButtonText: 'Aceptar'
            });
        }
    })
    .catch(() => {
        Swal.fire({
            title: 'Error de conexión',
            text: 'No se pudo conectar con el servidor. Intente de nuevo.',
            icon: 'error',
            confirmButtonText: 'Aceptar'
        });
    })
    .finally(() => {
        btn.disabled = false;
    });
}
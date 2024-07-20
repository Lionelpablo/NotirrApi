MétodosDescripción

.then(resolve)              Ejecuta la función callback resolve cuando la promesa se cumple.
.catch(reject)              Ejecuta la función callback reject cuando la promesa se rechaza.
.then(resolve,reject)       Método equivalente a las dos anteriores en el mismo .then().
.finally(end)               Ejecuta la función callback end tanto si se cumple como si se rechaza.

-------------------------------------------------------------

fetch("/url").then(function(response) {
    /* Código a realizar cuando se cumpla la promesa */
  });

  fetch("127.0.0.1:5000").then(function(response) {
    /* Código a realizar cuando se cumpla la promesa */
  });

-------------------------------------------------------------

  fetch("/url")
  .then(function(response) {
    /* Código a realizar cuando se cumpla la promesa */
  })
  .catch(function(error) {
    /* Código a realizar cuando se rechaza la promesa */
  });

  -------------------------------------------------------------

  fetch("/url")
  .then(response => {
    return response.text(); // Devuelve una promesa
  })
  .then(data => {
    console.log(data);
  })
  .catch(error => { /* Código a realizar cuando se rechaza la promesa */ });



  -------------------------------------------------------------

  https://lenguajejs.com/javascript/asincronia/promesas/
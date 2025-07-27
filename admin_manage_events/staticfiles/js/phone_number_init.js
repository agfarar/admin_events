document.addEventListener('DOMContentLoaded', function() {
  // Inicializar intlTelInput
  var input = document.querySelector("#id_phone_number");
  var iti = window.intlTelInput(input, {
    separateDialCode: true,
    initialCountry: 'auto',
  });

  // Función para actualizar el valor del campo con el indicativo del país seleccionado
  function updateDialCode() {
    var phoneNumberInput = document.querySelector('input[name="phone_number"]');
    var countryCode = iti.getSelectedCountryData().dialCode;
    input.value = '+' + countryCode + phoneNumberInput.value;
  }

  // Llamar a la función inicialmente para establecer el valor inicial del campo
  updateDialCode();

  // Suscribirse al evento countrychange usando iti.listen
  iti.promise.then(function() {
    iti.listen('countrychange', function() {
      updateDialCode(); // Actualizar el valor del campo cuando cambia el país seleccionado
    });
  });
});
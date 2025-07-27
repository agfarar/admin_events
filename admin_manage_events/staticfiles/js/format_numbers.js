document.addEventListener('DOMContentLoaded', function() {
    const priceFields = document.querySelectorAll('input[name=price], input[name=price_category_sold]');

    priceFields.forEach(field => {
        field.addEventListener('input', function(event) {
            let value = event.target.value.replace(/[^0-9]/g, ''); // Eliminar todo lo que no sea dígito
            if (value === '') {
                event.target.value = '';
                return;
            }
            event.target.value = value.replace(/\B(?=(\d{3})+(?!\d))/g, ','); // Formatear con puntos cada 3 dígitos
        });
    });
});

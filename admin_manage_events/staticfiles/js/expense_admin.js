document.addEventListener('DOMContentLoaded', function() {
    /**
     * Actualiza el precio en la fila basado en la cantidad y el precio del inventario seleccionado.
     * @param {HTMLElement} row - La fila (tr) que contiene los inputs de cantidad y precio.
     */
    function updatePrice(row) {
        if (!row) {
            console.log('Fila no encontrada');
            return;
        }

        const quantityInput = row.querySelector('input[name$="-quantity"]');
        const priceInput = row.querySelector('input[name$="-price"]');
        const inventorySelect = row.querySelector('select[name$="-inventory_item"]');

        if (!quantityInput || !priceInput || !inventorySelect) {
            console.log('Inputs no encontrados en la fila');
            return;
        }

        const selectedOption = inventorySelect.options[inventorySelect.selectedIndex];
        const priceText = selectedOption.textContent.match(/\$([0-9.,]+)/);

        let price = 0;
        if (priceText) {
            price = parseFloat(priceText[1].replace(',', ''));
            console.log(`Precio extraído: ${price}`);
        } else {
            console.log('No se pudo extraer el precio');
        }

        const quantity = parseFloat(quantityInput.value) || 0;
        const totalPrice = (price * quantity).toFixed(2);
        priceInput.value = totalPrice;

        console.log(`Fila actual - Cantidad: ${quantity}, Precio: ${price}, Total fila: ${totalPrice}`);

        // Actualiza el total después de modificar el precio de la fila
        updateTotal();
    }

    /**
     * Calcula y actualiza el total de todos los precios en la tabla.
     */
    function updateTotal() {
        let total = 0;

        // Iterar sobre cada fila y sumar los valores de los inputs de precio
        document.querySelectorAll('tr.form-row').forEach(row => {
            const priceInput = row.querySelector('input[name$="-price"]');
            if (priceInput) {
                const value = parseFloat(priceInput.value) || 0;
                total += value;
            } else {
                console.log('Input de precio no encontrado en la fila');
            }
        });

        // Actualiza el valor del input con id "id_amount" con el total calculado
        const amountInput = document.querySelector('#id_amount');
        if (amountInput) {
            amountInput.value = total.toFixed(2);
            console.log(`Total final: ${amountInput.value}`);
        } else {
            console.log('Input de total no encontrado');
        }
    }

    /**
     * Añade eventos para actualizar los precios y el total cuando se cambien los inputs.
     */
    function addEventListeners() {
        const inventorySelects = document.querySelectorAll('select[name$="-inventory_item"]');
        const quantityInputs = document.querySelectorAll('input[name$="-quantity"]');
        const deleteLinks = document.querySelectorAll('td.delete a.inline-deletelink');

        inventorySelects.forEach(select => select.addEventListener('change', function() {
            const row = select.closest('tr');
            console.log('Cambio en select de inventario');
            updatePrice(row);
        }));

        quantityInputs.forEach(input => input.addEventListener('input', function() {
            const row = input.closest('tr');
            console.log('Cambio en input de cantidad');
            updatePrice(row);
        }));

        deleteLinks.forEach(link => link.addEventListener('click', function(event) {
            event.preventDefault(); // Evita el comportamiento por defecto del enlace

            const row = link.closest('tr');
            if (row) {
                row.remove(); // Elimina la fila
                console.log('Fila eliminada');
                updateTotal(); // Actualiza el total después de eliminar la fila
            } else {
                console.log('Fila no encontrada para eliminar');
            }
        }));
    }

    /**
     * Inicializa los eventos y actualiza los precios y el total al cargar la página.
     */
    function initialize() {
        addEventListeners();

        // Actualiza los precios para las filas existentes al cargar la página
        document.querySelectorAll('tr.form-row').forEach(row => {
            console.log('Inicializando fila');
            updatePrice(row);
        });

        // Actualiza el total después de la inicialización
        console.log('Inicializando total');
        updateTotal();
    }

    initialize();

    // Actualiza los eventos y el total cuando se añadan nuevas filas
    document.querySelector('#expense_items-group').addEventListener('click', function(event) {
        if (event.target && event.target.matches('.add-row a')) {
            console.log('Fila añadida');
            setTimeout(() => {
                addEventListeners(); // Añade eventos a la nueva fila
                updateTotal(); // Actualiza el total después de agregar nuevas filas
            }, 100);
        }
    });

    // Recalcular el total cuando se elimine una fila
    const observer = new MutationObserver(() => {
        updateTotal();
    });

    observer.observe(document.querySelector('#expense_items-group'), { childList: true, subtree: true });

    /**
     * Asegura que el valor del campo #id_amount esté actualizado antes de enviar el formulario.
     */
    function updateAmountBeforeSubmit(event) {
        updateTotal(); // Actualiza el total antes de enviar el formulario
    }

    // Añade un listener al evento submit del formulario
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', updateAmountBeforeSubmit);
    }
});

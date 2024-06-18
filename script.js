
    const xhr = new XMLHttpRequest();
    xhr.open('GET', 'http://192.168.1.4:8000/active_product', false);
    xhr.send(null);


        const product = JSON.parse(xhr.responseText);


        const productId = product.is_active;
        const currentPrice = product.price;

        const priceCurrent = document.getElementById('current-price');
        priceCurrent.innerText = currentPrice;

        const priceInput = document.getElementById('new-price');



        // Подключаемся к WebSocket с использованием productId
        const ws = new WebSocket(`ws://192.168.1.4:8000/ws/${productId}`);

        ws.onmessage = function(event) {

            const data = event.data;
            console.log(data);
            document.getElementById('current-price').innerText = data.split(' ')[1];

        };

        function placeBid() {
            const input = document.getElementById("new-price");
            const newPrice = input.value;
            ws.send(newPrice);
            input.value = 5;
        }

        // Добавляем обработчики для кнопок
        document.getElementById('decrement').addEventListener('click', () => {
            let currentValue = parseInt(priceInput.value);
            if (currentValue > 5) {
                priceInput.value = currentValue - 5;
            }
        });

        document.getElementById('increment').addEventListener('click', () => {
            let currentValue = parseInt(priceInput.value);
            if (currentValue < 100) {
                priceInput.value = currentValue + 5;

            }
        });


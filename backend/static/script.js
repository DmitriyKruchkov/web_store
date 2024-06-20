

        const priceCurrent = document.getElementById('current-price');
        const priceInput = document.getElementById('new-price');

        function getCookie(name) {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if (parts.length === 2) return parts.pop().split(';').shift();
    }
          const token = getCookie('access_token');
          console.log(token);
          const ws = new WebSocket(`ws://${window.location.host}/ws?access_token=${token}`);
        ws.onmessage = function(event) {

            const data = JSON.parse(event.data);
            console.log(data);
            document.getElementById('current-price').innerText = data.price;
            document.getElementById('owner').innerText = data.address;

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


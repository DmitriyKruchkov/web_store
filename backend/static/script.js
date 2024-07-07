
        const progressBar = document.getElementById('progress-bar');
        let width = 100; // Initial width in percentage
        const interval = 11000; // Time interval in milliseconds
        const priceCurrent = document.getElementById('current-price');
        const priceInput = document.getElementById('new-price');
        function updateProgressBar() {
            if (width > 0) {
                width -= 1;
                progressBar.style.width = width + '%';

                if (width > 50) {
                    progressBar.style.backgroundColor = 'green';
                } else if (width > 25) {
                    progressBar.style.backgroundColor = 'yellow';

                } else if (width == 0) {
                    console.log('here')
                    window.location.href = window.location.href;
                }
                else {
                    progressBar.style.backgroundColor = 'red';
                }
            }
        }

        setInterval(updateProgressBar, interval / 100);
        function getCookie(name) {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if (parts.length === 2) return parts.pop().split(';').shift();
    }
          const access_token = getCookie('access_token');


          const ws = new WebSocket(`ws://${window.location.host}/ws?access_token=${access_token}`);
            function updatePrice(newPrice) {
                const priceElement = document.getElementById('current-price');


                priceElement.textContent = newPrice;


                priceElement.style.color = 'green';


        setTimeout(() => {
            priceElement.style.color = '';
        }, 2000);
    }
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            console.log('getMessage');
            const active_id = getCookie('active_id');

            width = data.progress_bar;
            console.log(width);
            const audio = document.getElementById('audio-player');
            audio.volume = 0.3;
            audio.pause()
            audio.play().catch(error => {
                console.error('Error attempting to play audio:', error);
            });
            document.getElementById('owner').innerText = data.address;
            updatePrice(data.price);

        };
        ws.onclose = function(event) {
            console.log('closed');
            window.location.href = '/stopped';
        };
        function updateClock(timezone) {
            const clockElement = document.getElementById('clock');
            const now = new Date();
            const options = {
                timeZone: timezone,
                day: '2-digit',
                month: '2-digit',
                year: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: false
            };
            const formatter = new Intl.DateTimeFormat([], options);
            const formattedTime = formatter.format(now);
            clockElement.textContent = formattedTime;
        }


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


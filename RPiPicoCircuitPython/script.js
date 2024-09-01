    const joystick = document.getElementById('joystick');
    const joystickContainer = document.getElementById('joystickContainer');
    const coordinatesDisplay = document.getElementById('coordinates');
    const car = document.getElementById('car');
    let lastX = 75, lastY = 75;
    let carPosX = window.innerWidth / 2 - 50;
    let carPosY = window.innerHeight / 2 - 25;

    function updateCarPosition(deltaX, deltaY) {
        carPosX += deltaX;
        carPosY += deltaY;
        car.style.left = `${carPosX}px`;
        car.style.top = `${carPosY}px`;
    }

    function getJoystickPosition(event) {
        const rect = joystickContainer.getBoundingClientRect();
        const offsetX = (event.touches ? event.touches[0].clientX : event.clientX) - rect.left;
        const offsetY = (event.touches ? event.touches[0].clientY : event.clientY) - rect.top;
        const x = Math.min(Math.max(offsetX - 25, 0), rect.width - 50);
        const y = Math.min(Math.max(offsetY - 25, 0), rect.height - 50);
        return { x, y };
    }

    function updateJoystickPosition(event) {
        const { x, y } = getJoystickPosition(event);
        joystick.style.left = `${x}px`;
        joystick.style.top = `${y}px`;
        return { x, y };
    }

    let currentPos = { x: 75, y: 75 };

    function handleMove(event) {
        event.preventDefault();
        currentPos = updateJoystickPosition(event);
    }

    function handleEnd() {
        joystick.style.left = '75px';
        joystick.style.top = '75px';
        currentPos = { x: 75, y: 75 };
    }

    joystickContainer.addEventListener('mousedown', handleMove);
    joystickContainer.addEventListener('mousemove', handleMove);
    joystickContainer.addEventListener('mouseup', handleEnd);
    joystickContainer.addEventListener('mouseleave', handleEnd);
    joystickContainer.addEventListener('touchstart', handleMove);
    joystickContainer.addEventListener('touchmove', handleMove);
    joystickContainer.addEventListener('touchend', handleEnd);

    setInterval(() => {
        if (lastX !== currentPos.x || lastY !== currentPos.y) {
            coordinatesDisplay.textContent = `X: ${currentPos.x}, Y: ${currentPos.y}`;
            updateCarPosition(currentPos.x - lastX, currentPos.y - lastY);
            lastX = currentPos.x;
            lastY = currentPos.y;
        }
    }, 500);

    document.getElementById('btnUp').addEventListener('click', () => updateCarPosition(0, -10));
    document.getElementById('btnDown').addEventListener('click', () => updateCarPosition(0, 10));
    document.getElementById('btnLeft').addEventListener('click', () => updateCarPosition(-10, 0));
    document.getElementById('btnRight').addEventListener('click', () => updateCarPosition(10, 0));

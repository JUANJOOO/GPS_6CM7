let map;
let puntoA, puntoB;
let ubicacionActualMarker;

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 19.4978, lng: -99.1269 }, // Ajusta a tus coordenadas iniciales
        zoom: 15,
    });

    map.addListener("click", (e) => {
        if (!puntoA) {
            puntoA = crearMarcador(e.latLng, "A");
            enviarPuntoAlServidor(puntoA.getPosition(), 'A');
        } else if (!puntoB) {
            puntoB = crearMarcador(e.latLng, "B");
            enviarPuntoAlServidor(puntoB.getPosition(), 'B');
        }
    });

    actualizarUbicacionYVerificarDesviacion(); // Comienza a actualizar la ubicación inmediatamente
}

function crearMarcador(position, label) {
    return new google.maps.Marker({
        position: position,
        label: label,
        map: map,
    });
}

function enviarPuntoAlServidor(position, tipo) {
    fetch('/establecer_punto_ab', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ [tipo]: { latitud: position.lat(), longitud: position.lng() } }),
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Error:', error));
}

function actualizarUbicacionYVerificarDesviacion() {
    fetch('/ultima_ubicacion')
    .then(response => response.json())
    .then(data => {
        if(data.latitud && data.longitud) {
            actualizarMarcadorUbicacionActual(data.latitud, data.longitud);
            enviarUbicacionParaVerificarDesviacion(data.latitud, data.longitud);
        }
    })
    .catch(error => console.error('Error:', error));

    setTimeout(actualizarUbicacionYVerificarDesviacion, 10000); // Actualiza cada 10 segundos
}

function actualizarMarcadorUbicacionActual(latitud, longitud) {
    const nuevaUbicacion = new google.maps.LatLng(latitud, longitud);

    if (!ubicacionActualMarker) {
        ubicacionActualMarker = new google.maps.Marker({
            position: nuevaUbicacion,
            map: map,
            icon: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'
        });
    } else {
        ubicacionActualMarker.setPosition(nuevaUbicacion);
    }
}

function enviarUbicacionParaVerificarDesviacion(latActual, lngActual) {
    fetch('/verificar_desviacion', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ latitud: latActual, longitud: lngActual }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.alerta) {
            alert("Alerta: Se ha desviado de la ruta.");
        }
    })
    .catch(error => console.error('Error:', error));
}

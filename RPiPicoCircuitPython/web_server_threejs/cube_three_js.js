/*
<!DOCTYPE html>
<html>
	<head>
		<title>My first three.js app</title>
		<style>
			body { margin: 0; }
		</style>
		<script src="https://cdn.jsdelivr.net/npm/three@0.126.1/build/three.min.js"></script>
	</head>
	<body>
        <div id="cube"></div>
        <h1>ARM</h1>
		<script type="module" >
*/		
			//import * as THREE from 'three';
	    console.log('Hello World')
            const width = window.innerWidth;
            const height = window.innerHeight/2;
			const scene = new THREE.Scene();
			const camera = new THREE.PerspectiveCamera( 75, width / height, 0.1, 1000 );

			const renderer = new THREE.WebGLRenderer();
			renderer.setSize( width, height );
			const arm_DOM = document.getElementById("cube");
			arm_DOM.appendChild( renderer.domElement );

			const geometry = new THREE.BoxGeometry( 1, 1, 1 );
			const material = new THREE.MeshBasicMaterial( { color: 0x00ff00 } );
			const cube = new THREE.Mesh( geometry, material );
			scene.add( cube );

			camera.position.z = 5;

			function animate() {
				requestAnimationFrame( animate );

				cube.rotation.x += 0.01;
				cube.rotation.y += 0.01;

				renderer.render( scene, camera );
			}

			animate();
		
/*
		</script>

	</body>
</html>
*/

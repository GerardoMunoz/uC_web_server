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
        <div id="arm"></div>
        <h1>ARM</h1>
		<div id="error"></div>
		<script  >
*/
        //import * as THREE from 'three';
			
        	console.log('Hello World')
		// Set up Three.js scene and camera
		const width = window.innerWidth;
		const height = window.innerHeight / 2;
		const scene = new THREE.Scene();
		const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
		camera.position.x = 0;
		camera.position.y = 5;
		camera.position.z = 0;
		camera.lookAt(0, 0, 0);

		// Define a point in 3D space
		const point = new THREE.Vector3();

		// Set initial LED color and arm dimensions
		let color_led = 0x00fff0;
		const a1 = 1;
		const a2 = 2;
		const a3 = 2;

		// Create WebGL renderer and append it to the DOM
		const renderer = new THREE.WebGLRenderer();
		renderer.setSize(width, height);
		const arm_DOM = document.getElementById("arm");
		arm_DOM.appendChild(renderer.domElement);

		// Define a small dot for visualization
		let dot = new THREE.BoxGeometry(0.01, 0.01, 0.01);

		// error label
		const error_DOM = document.getElementById("error");
		error_DOM.innerHTML = "Error="

		// Set up the base of the mechanical arm
		let geometry = new THREE.BoxGeometry(0.2, a1, 0.2);
		let material = new THREE.MeshBasicMaterial({ color: color_led });
		const base = new THREE.Mesh(geometry, material);
		base.translateY(a1 / 2);
		scene.add(base);

		// Create hierarchical structure for the arm segments
		let shoulder = new THREE.Object3D();
		shoulder.translateY(a1 / 2);
		base.add(shoulder);

		geometry = new THREE.BoxGeometry(0.05, a2, 0.05);
		let lowerArm = new THREE.Mesh(geometry, material);
		lowerArm.translateY(a2 / 2);
		shoulder.add(lowerArm);

		let elbow = new THREE.Object3D();
		elbow.translateY(a2 / 2);
		lowerArm.add(elbow);

		geometry = new THREE.BoxGeometry(0.05, a3, 0.05);
		let arm = new THREE.Mesh(geometry, material);
		arm.translateY(a3 / 2);
		elbow.add(arm);

		let wrist = new THREE.Object3D();
		wrist.translateY(a3 / 2);
		arm.add(wrist);

		// Create a hand at the end of the arm
		geometry = new THREE.TorusGeometry(0.1, 0.01, 3, 9, 5.6);
		let hand = new THREE.Mesh(geometry, material);
		hand.rotation.y = Math.PI / 2;
		hand.rotation.x = Math.PI / 2;
		wrist.add(hand);

		// Set up parameters for a line to visualize the arm trajectory
		const MAX_POINTS = 1000;
		material = new THREE.LineBasicMaterial({ color: 0x0000ff });
		geometry = new THREE.BufferGeometry();
		const positions = new Float32Array(MAX_POINTS * 3);
		let last_point = 0;

		// Set initial positions for the arm trajectory line
		geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
		const line = new THREE.Line(geometry, material);
		scene.add(line);

		// Define two points for the Bezier curve
		const P0 = new THREE.Vector3(a2, a1 / 2, -a3);
		const P1 = new THREE.Vector3(a2, a1 / 2, a3);
		var t = 0;

		var P0_camara = new THREE.Vector3(0, 5, 0);
		var P1_camara = new THREE.Vector3(0, 0, 5);
		var t_camara=0
		

		// Start the animation loop
		animate();

		function animate() {
			
			
			//if (t <= 1) {
				requestAnimationFrame(animate);
			//}
			
			// Calculate inverse kinematics and update arm positions
			let th1p, th2p, th3p, R;
			R = bezier2(P0, P1, t);
			[th1p, th2p, th3p] = inv_kin(R);
			// Loop through the Bezier curve parameter
			if (t <= 1) {
				t = t + 0.01;
			}


			base.rotation.y = th1p;
			shoulder.rotation.z = Math.PI / 2 + th2p;
			elbow.rotation.z = th3p;

			// Visualize the position of the wrist with a dot
			let dot_i = new THREE.Mesh(dot, material);
			wrist.getWorldPosition(point);
			scene.add(dot_i);

			// Update the arm trajectory line
			positions[last_point] = point.x;
			positions[last_point + 1] = point.y;
			positions[last_point + 2] = point.z;
			last_point = last_point + 3;
			line.geometry.attributes.position.needsUpdate = true;
			error_DOM.innerHTML = "Error="+R.distanceTo(point)
			
			R_camara = bezier2(P0_camara, P1_camara, t_camara);
			camera.position.set(R_camara.x,R_camara.y,R_camara.z)
			//console.log(camera.position)
			camera.lookAt(0, 0, 0)
			if (t_camara <= 1) {
				t_camara = t_camara + 0.00033;
			}
			else {
				t_camara = 0
			}

			// Render the scene
			renderer.render(scene, camera);




		}

		// Function to turn the LED on
		function led_on() {
			material.color.setRGB(1, 1, 1);
		}

		// Function to turn the LED off
		function led_off() {
			material.color.setRGB(0, 0, 1);
		}

		// Function to quit or reset
		function quit() {
			material.color.setRGB(0, 0, 0);
		}

		// Function to calculate inverse kinematics
		function inv_kin(P) {
			const x03 = -P.x;
			const z03 = P.y;
			const y03 = P.z;
			const th1 = Math.atan2(y03, x03);
			const r1 = Math.sqrt(x03 ** 2 + y03 ** 2);
			const r2 = -(z03 - a1);
			const phi2 = Math.atan2(r2, r1);
			const r3 = Math.sqrt(r1 ** 2 + r2 ** 2);
			const phi1 = Math.acos((a3 ** 2 - a2 ** 2 - r3 ** 2) / (-2 * a2 * r3));
			const th2 = phi2 - phi1;
			const phi3 = Math.acos((r3 ** 2 - a2 ** 2 - a3 ** 2) / (-2 * a2 * a3));
			const th3 = Math.PI - phi3;
			return [th1, th2, th3];
		}

		// Function for Bezier interpolation between two points
		function bezier2(P0, P1, t) {
			const R = P0.clone().multiplyScalar(1 - t).add(P1.clone().multiplyScalar(t));
			return R;
		}
		
/*
		</script>

	</body>
</html>
*/

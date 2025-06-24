document.addEventListener('DOMContentLoaded', function() {
    // Existing elements
    const modeStatus = document.getElementById('mode-status');
    const moodStatus = document.getElementById('mood-status');
    const sceneStatus = document.getElementById('scene-status');
    const sceneSelector = document.getElementById('scene-selector');

    const idleModeButton = document.getElementById('idle-mode-button');
    const assistModeButton = document.getElementById('assist-mode-button');
    const chatModeButton = document.getElementById('chat-mode-button');

    // For Lumen visual state
    const mainTitle = document.querySelector('h1'); // Assuming there's only one h1 for the main title
    const bodyElement = document.body;
    const statusContainer = document.getElementById('status-container'); // For glitch effect

    let scenes = ["default", "work", "relax"]; // Initial scenes

    function populateSceneSelector(currentScene = "default") {
        let sceneExists = scenes.includes(currentScene);
        if (!sceneExists && currentScene) {
            scenes.push(currentScene);
        }
        scenes.sort();

        sceneSelector.innerHTML = ''; // Clear before repopulating
        scenes.forEach(scene => {
            const option = document.createElement('option');
            option.value = scene;
            option.textContent = scene.charAt(0).toUpperCase() + scene.slice(1);
            sceneSelector.appendChild(option);
        });
        sceneSelector.value = currentScene;
    }

    async function updateRegularState() {
        try {
            const response = await fetch('http://localhost:8000/state');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status} for /state`);
            }
            const data = await response.json();

            modeStatus.textContent = data.mode || 'N/A';
            moodStatus.textContent = data.mood || 'N/A';
            sceneStatus.textContent = data.scene || 'N/A';

            if (data.scene && !scenes.includes(data.scene)) {
                scenes.push(data.scene);
                populateSceneSelector(data.scene);
            } else {
                sceneSelector.value = data.scene || 'default';
            }

        } catch (error) {
            console.error("Error fetching regular state:", error);
            modeStatus.textContent = 'Error';
            moodStatus.textContent = 'Error';
            sceneStatus.textContent = 'Error';
        }
    }

    async function updateLumenVisualState() {
        try {
            const response = await fetch('http://localhost:8000/lumen_visual_state');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status} for /lumen_visual_state`);
            }
            const visualData = await response.json();

            // Apply base colors
            if (mainTitle && visualData.highlightColor) {
                mainTitle.style.color = visualData.highlightColor;
            }

            // Clear previous border color style if effect will handle it, or apply base border
            if (bodyElement && visualData.borderColor) {
                 // Reset direct border style to allow class-based effects to take over border color
                bodyElement.style.borderTop = '';
                bodyElement.style.borderBottom = '';
                bodyElement.style.paddingLeft = ''; // Reset padding if not managed by effect class
                bodyElement.style.paddingRight = '';

                // Default border if no specific effect is overriding it
                if (!visualData.borderEffect || visualData.borderEffect === "none") {
                     bodyElement.style.borderTop = `5px solid ${visualData.borderColor}`;
                     bodyElement.style.borderBottom = `5px solid ${visualData.borderColor}`;
                     bodyElement.style.paddingLeft = '10px';
                     bodyElement.style.paddingRight = '10px';
                }
            }

            // Handle Border Effects
            if (bodyElement && typeof visualData.borderEffect !== 'undefined') { // Check if borderEffect is defined
                bodyElement.classList.remove('body-pulse-magenta', 'body-flicker-blood-orange'); // Remove old effects
                if (visualData.borderEffect === "pulseMagenta") {
                    bodyElement.classList.add('body-pulse-magenta');
                } else if (visualData.borderEffect === "flickerBloodOrange") {
                    bodyElement.classList.add('body-flicker-blood-orange');
                }
                // If "none", all relevant classes are already removed.
            }

            // Handle Popup Effects (conceptual on #status-container)
            if (statusContainer && typeof visualData.popupEffect !== 'undefined') { // Check if popupEffect is defined
                statusContainer.classList.remove('glitch-effect'); // Remove old effect
                if (visualData.popupEffect === "glitch") {
                    statusContainer.classList.add('glitch-effect');
                }
            }

            // Handle Scanline Overlay (conceptual on body)
            if (bodyElement && typeof visualData.scanlineOverlay !== 'undefined') {
                if (visualData.scanlineOverlay) {
                    bodyElement.classList.add('scanline-overlay');
                } else {
                    bodyElement.classList.remove('scanline-overlay');
                }
            }

            console.log(`Lumen visual state received:`, visualData);

        } catch (error) {
            console.error("Error fetching Lumen visual state:", error);
            if (mainTitle) mainTitle.style.color = 'initial';
            if (bodyElement) {
                bodyElement.style.borderTop = 'none'; // Clear specific inline styles
                bodyElement.style.borderBottom = 'none';
                bodyElement.style.paddingLeft = '';
                bodyElement.style.paddingRight = '';
                bodyElement.classList.remove('body-pulse-magenta', 'body-flicker-blood-orange', 'scanline-overlay');
            }
            // const statusContainer = document.getElementById('status-container'); // Already defined
            if (statusContainer) statusContainer.classList.remove('glitch-effect');
        }
    }

    async function setMode(mode) {
        try {
            const response = await fetch(`http://localhost:8000/mode/${mode}`, {
                method: 'POST',
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            await response.json();
            updateRegularState();
            updateLumenVisualState();
        } catch (error) {
            console.error(`Error setting mode to ${mode}:`, error);
        }
    }

    async function setScene(sceneName) {
        try {
            const response = await fetch(`http://localhost:8000/scene/${sceneName}`, {
                method: 'POST',
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            await response.json();
            updateRegularState();
            updateLumenVisualState();
        } catch (error) {
            console.error(`Error setting scene to ${sceneName}:`, error);
        }
    }

    // Event Listeners
    idleModeButton.addEventListener('click', () => setMode('idle'));
    assistModeButton.addEventListener('click', () => setMode('assist'));
    chatModeButton.addEventListener('click', () => setMode('chat'));
    sceneSelector.addEventListener('change', (event) => setScene(event.target.value));

    // Initial population and status updates
    populateSceneSelector();
    updateRegularState();
    updateLumenVisualState();

    // Periodic updates
    setInterval(() => {
        updateRegularState();
        updateLumenVisualState();
    }, 5000);
});

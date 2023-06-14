document.addEventListener("DOMContentLoaded", function () {
    const startButton = document.querySelector("#user-input button:nth-child(1)");
    const stopButton = document.querySelector("#user-input button:nth-child(2)");
    const responseDiv = document.querySelector("#response");

    let recognition;
    let isListening = false;

    startButton.addEventListener("click", startListening);
    stopButton.addEventListener("click", stopListening);

    function startListening() {
        if (isListening) return;

        recognition = new webkitSpeechRecognition(); // Create a speech recognition instance
        recognition.continuous = true; // Keep listening until stopped
        recognition.interimResults = true; // Get intermediate results

        recognition.onstart = function () {
            isListening = true;
            startButton.disabled = true;
            stopButton.disabled = false;
            responseDiv.innerHTML = "Listening...";
        };

        recognition.onresult = function (event) {
            const transcript = event.results[event.results.length - 1][0].transcript;
            console.log("You:", transcript);
            sendUserInput(transcript);
        };

        recognition.onerror = function (event) {
            console.error("Error:", event.error);
        };

        recognition.onend = function () {
            isListening = false;
            startButton.disabled = false;
            stopButton.disabled = true;
            responseDiv.innerHTML = "Stopped listening.";
        };

        recognition.start();
    }

    function stopListening() {
        if (!isListening) return;

        recognition.stop();
    }

    function sendUserInput(input) {
        responseDiv.innerHTML = "You: " + input;

        // Send the user input to the server using an HTTP request (e.g., fetch or XHR)
        // Replace this with your own server endpoint
        fetch("/process-input", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ input }),
        })
            .then(response => response.json())
            .then(data => {
                handleResponse(data.response);
            })
            .catch(error => {
                console.error("Error:", error);
            });
    }

    function handleResponse(response) {
        responseDiv.innerHTML += "<br>Assistant: " + response;

        // Synthesize the response using the Web Speech API
        const speechSynthesis = window.speechSynthesis;
        const utterance = new SpeechSynthesisUtterance(response);
        speechSynthesis.speak(utterance);
    }
});

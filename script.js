const bgVideo = document.getElementById('bgVideo');
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const captureButton = document.getElementById('capture');
const pauseButton = document.getElementById('pause');
const resumeButton = document.getElementById('resume');
const voiceCommandButton = document.getElementById('voiceCommand');
const resultText = document.getElementById('result');
const musicPlayer = document.getElementById('musicPlayer');
const musicSource = document.getElementById('musicSource');
const volumeSlider = document.getElementById('volumeSlider');

// ✅ Mood Tips (GLOBAL)
const tips = {
    happy: "Keep smiling and spread the joy around! 😊",
    sad: "Take a deep breath and do something you love. 💙",
    fear: "Fear is temporary. You are stronger than you think. 💪",
    angry: "Pause. Breathe. You are in control. 💢➞️🌈",
    frustrated: "Step back. Recharge. You’ve got this! 🔁🔥",
    neutral: "A calm mind is a powerful mind. Stay centered. 🧘‍♂️",
    surprise: "Embrace the unexpected – that’s where magic happens! ✨",
    disgust: "It’s okay to step away. You deserve peace and comfort. 🌿"
};

// Volume control
musicPlayer.volume = volumeSlider.value;
volumeSlider.addEventListener('input', () => {
    musicPlayer.volume = volumeSlider.value;
});

// Webcam setup
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => {
        console.error("Error accessing webcam: ", err);
        alert("Webcam access denied. Please allow webcam permission.");
    });

// Emotion Detection
captureButton.addEventListener('click', () => {
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL('image/jpeg');

    fetch('/detect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: imageData })
    })
    .then(res => res.json())
    .then(data => {
        const emotion = data.emotion.toLowerCase();
        resultText.textContent = `Mood: ${emotion}`;

        if (tips[emotion]) {
            document.getElementById("emotion-tips").textContent = tips[emotion];
        }

        // Reset all emotion background classes
        document.body.className = document.body.className
            .split(' ')
            .filter(cls => !cls.endsWith('-bg'))
            .join(' ');

        // Add new background class
        document.body.classList.add(`${emotion}-bg`);

        const emotionVideos = {
            happy: 'static/bg/happy.mp4',
            sad: 'static/bg/sad.mp4',
            angry: 'static/bg/angry.mp4',
            fear: 'static/bg/fear.mp4',
            disgust: 'static/bg/disgust.mp4',
            neutral: 'static/bg/neutral.mp4',
            surprise: 'static/bg/happy.mp4'
        };

        if (emotion in emotionVideos) {
            bgVideo.src = emotionVideos[emotion];
            bgVideo.load();
            bgVideo.play();
        }

        if (data.music) {
            musicSource.src = data.music;
            musicPlayer.load();
            musicPlayer.style.display = 'block';
            musicPlayer.volume = volumeSlider.value;
            musicPlayer.play();
        } else {
            resultText.textContent = `Mood: ${emotion}`;
            showEmojis(emotion);
        }
    })
    .catch(err => {
        console.error('Detection error:', err);
        resultText.textContent = 'Error detecting emotion.';
    });
});

pauseButton.addEventListener('click', () => {
    musicPlayer.pause();
});

resumeButton.addEventListener('click', () => {
    musicPlayer.play();
});

// Voice Command Button Logic
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition;

if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript.trim().toLowerCase();
        console.log("Voice command:", transcript);

        if (transcript.includes("pause")) {
            musicPlayer.pause();
        } else if (transcript.includes("play") || transcript.includes("resume")) {
            musicPlayer.play();
        } else {
            alert(`Unrecognized command: ${transcript}`);
        }
    };

    recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
    };

    voiceCommandButton.addEventListener('click', () => {
        recognition.start();
        console.log("Voice recognition started...");
    });
} else {
    voiceCommandButton.disabled = true;
    alert("Speech Recognition is not supported in this browser.");
}

function showEmojis(emotion) {
    const emojiMap = {
        happy: "😊",
        sad: "😢",
        angry: "😠",
        neutral: "😐",
        fearful: "😨",
        disgust: "🤢",
        surprise: "😲"
    };

    const emoji = emojiMap[emotion] || "🙂";
    const container = document.getElementById('emoji-container');

    for (let i = 0; i < 10; i++) {
        const span = document.createElement('span');
        span.classList.add('emoji');
        span.textContent = emoji;
        span.style.left = Math.random() * 90 + "%";
        span.style.top = "80%";
        container.appendChild(span);
        setTimeout(() => span.remove(), 3000);
    }
}

function startLiveDetection() {
    setInterval(() => {
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        const imageData = canvas.toDataURL('image/jpeg');

        fetch('/detect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageData })
        })
        .then(res => res.json())
        .then(data => {
            const emotion = data.emotion.toLowerCase();
            resultText.textContent = `Mood: ${emotion}`;

            if (tips[emotion]) {
                document.getElementById("emotion-tips").textContent = tips[emotion];
            }

            if (data.youtube) {
                document.getElementById("musicPlayer").style.display = "none";
                document.getElementById("ytFrame").src = data.youtube;
                document.getElementById("ytFrame").style.display = "block";
            }
        });
    }, 10000); // Every 10 seconds
}

startLiveDetection();

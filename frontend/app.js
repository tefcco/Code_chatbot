const codePanel = document.getElementById("codePanel");
const codeToggleBtn = document.getElementById("codeToggleBtn");
const sendBtn = document.getElementById("sendBtn");
const chatArea = document.getElementById("chatArea");

function toggleCodePanel() {
    const isHidden = codePanel.classList.contains("hidden");

    if (isHidden) {
        codePanel.classList.remove("hidden");
        codeToggleBtn.classList.add("active");
    } else {
        codePanel.classList.add("hidden");
        codeToggleBtn.classList.remove("active");
    }
}

function addMessage(content, sender) {
    const message = document.createElement("div");
    message.classList.add("message", sender);

    const bubble = document.createElement("div");
    bubble.classList.add("bubble");
    bubble.textContent = content;

    message.appendChild(bubble);
    chatArea.appendChild(message);

    chatArea.scrollTop = chatArea.scrollHeight;

    return bubble;
}

async function submitReview() {
    const code = document.getElementById("codeInput").value;
    const language = document.getElementById("language").value;
    const personality = document.getElementById("personality").value;

    if (!code.trim()) {
        alert("Molimo vas unesite kod pre slanja.");
        return;
    }
    const preview = code.length > 80 ? code.slice(0, 80) + "..." : code;
    addMessage(preview, "user");

    codePanel.classList.add("hidden");
    codeToggleBtn.classList.remove("active");
    sendBtn.disabled = true;

    const botBubble = addMessage("", "bot");
    botBubble.classList.add("loading");

    try {
        const response = await fetch("/api/review", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ code, language, personality }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Nepoznata greska.");
        }

        const data = await response.json();

        botBubble.classList.remove("loading");
        botBubble.textContent = data.review;

    } catch (err) {
        botBubble.classList.remove("loading");
        botBubble.textContent = `Greska: ${err.message}`;
        botBubble.style.color = "#ff6b6b";
    } finally {
        sendBtn.disabled = false;
        document.getElementById("codeInput").value = "";
    }
}
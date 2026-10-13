function createMessageBubble() {
    const messages = document.querySelector("#messages");

    const chatRow = document.createElement("div");
    chatRow.className = "chat chat-end";

    const bubble = document.createElement("h2");
    bubble.id = "message";
    bubble.className =
        "chat-bubble px-6 py-4 chat-bubble-dynamic-shadow text-base scroll-mb-[170px] lg:px-10 lg:py-6 lg:text-lg font-mono text-base-content leading-normal lg:leading-10 -translate-x-5 lg:-translate-x-15 -translate-y-2";

    let userMessage = document.getElementById("message-input");
    let userMessageText = userMessage.value;
    userMessage.value = "";
    bubble.textContent = userMessageText;

    const userName = document.getElementById("username").value;
    const footer = document.createElement("div");
    footer.className =
        "chat-footer text-left text-lg lg:text-2xl font-mono px-1 py-0.5 lg:p-2 bg-base-300 border-2 rounded-xl border-base-content/60 translate-x-6 lg:-translate-x-0";
    footer.textContent = userName;

    chatRow.appendChild(bubble);
    chatRow.appendChild(footer);
    messages.appendChild(chatRow);

    return bubble;
}

function createLoadingSpinner() {
    const messages = document.querySelector("#messages");

    const chatRow = document.createElement("div");
    chatRow.className = "chat chat-start";

    const loadingSpinner = document.createElement("span");
    loadingSpinner.id = "loading";
    loadingSpinner.className = "loading loading-spinner loading-xl scroll-mb-[100px] translate-x-2 lg:translate-x-6";

    chatRow.appendChild(loadingSpinner);
    messages.appendChild(chatRow);

    return loadingSpinner;
}

function createBotBubble() {
    const messages = document.querySelector("#messages");

    const chatRow = document.createElement("div");
    chatRow.className = "chat chat-start";

    const bubble = document.createElement("h2");
    bubble.id = "response";
    bubble.className =
        "chat-bubble px-6 py-4 chat-bubble-dynamic-shadow text-base scroll-mt-20 lg:px-10 lg:py-6 lg:text-lg font-mono text-base-content leading-normal lg:leading-10 translate-x-5 lg:translate-x-15 -translate-y-2";

    const footer = document.createElement("div");
    footer.className =
        "chat-footer text-left text-lg lg:text-2xl font-mono px-1 py-0.5 lg:p-2 bg-base-300 border-2 rounded-xl border-base-content/60 -translate-x-6 lg:translate-x-0";
    footer.textContent = "Bot";

    chatRow.appendChild(bubble);
    chatRow.appendChild(footer);
    messages.appendChild(chatRow);

    return bubble;
}
let chatId = null
async function streamMessagePayload(endpoint, payload) {
    let userBubble = createMessageBubble();
    userBubble.scrollIntoView({
        behavior: "smooth",
        block: "end"
    });
    let loadingSpinner = createLoadingSpinner();
    loadingSpinner.scrollIntoView({
        behavior: "smooth",
        block: "end"
    });

    // Dispatch POST request
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    });
    // Check if the browser followed a redirect (e.g., POST /chat -> GET /login)
    if (response.redirected) {
        // Redirect the entire browser window to the login page
        window.location.href = response.url;
        return;
    }
    if (!response.ok) {
        let errorMessage = document.getElementById("limit-error");
        errorMessage.removeAttribute("hidden");
        throw new Error(`Request failed: ${response.status}`);
    }

    chatId = response.headers.get("Chat-ID");

    // Initialize stream reader and UTF-8 text decoder
    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');

    let responseContainer = createBotBubble();

    let responseText = "";
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunkText = decoder.decode(value, { stream: true })
        // Stream repsonse text to chat bubble and auto-scroll
        responseText += chunkText;
        responseContainer.innerHTML = marked.parse(responseText);
    }
    loadingSpinner.remove();
    responseContainer.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("#messages .chat-bubble").forEach((bubble) => {
        bubble.innerHTML = marked.parse((bubble.textContent || "").trimStart());
        bubble.scrollIntoView({
            behavior: "instant",
            block: "end"
        });
    });
    scrollBy(0, 180, {
        behavior: "smooth",
    });

    const form = document.querySelector("#chat-form");
    const input = document.querySelector("#message-input");
    const modelSelection = document.getElementById("model");
    const systemPrompt = document.getElementById("sys_prompt");
    chatId = document.getElementById("chat-id").value || null;
    let msgCount = 0;

    input.addEventListener("keydown", (event) => {
        if ((event.key === "Enter") && !(event.shiftKey)) {
            event.preventDefault();
            event.target.form.requestSubmit();
        }
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const message = input.value.trim();
        if (!message) return;

        const model = modelSelection.value;
        if (!model) return;
        const sys_prompt = systemPrompt.value;
        if (!sys_prompt) return;

        if (msgCount == 0) {
            var chatExists = false;
        }
        else {
            var chatExists = true;
        }

        if (chatId) {
            chatExists = true;
            var payload = {
                "message": message,
                "settings": {
                    "model": model,
                    "sys_prompt": sys_prompt,
                    "chat_id": chatId
                },
                "existing_chat": chatExists
            }
        }
        else {
            var payload = {
                "message": message,
                "settings": {
                    "model": model,
                    "sys_prompt": sys_prompt
                },
                "existing_chat": chatExists
            }
        }
        console.log(payload);
        input.disabled = true;
        await streamMessagePayload("/chat", payload);
        input.disabled = false;
        input.focus();
        msgCount += 1;
    });
});
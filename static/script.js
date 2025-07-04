document.addEventListener("DOMContentLoaded", function () {
    const products = ["LIP", "EYELINER", "EYESHADOW", "FOUNDATION", "BLUSH", "HIGHLIGHTER"];
    const productSettings = {};
    const productList = document.getElementById("product-list");

    window.startCamera = function () {
        document.getElementById("start-btn").style.display = "none";
        document.getElementById("controls").style.display = "block";
        document.getElementById("extra-options").style.display = "block";
        document.getElementById("camera").src = "/video_feed";

        renderControls();
    };

    function createSlider(min, max, value, step = 1) {
        const s = document.createElement("input");
        s.type = "range";
        s.min = min;
        s.max = max;
        s.step = step;
        s.value = value;z
        s.style.margin = "0 5px";
        return s;
    }

    function renderControls() {
        productList.innerHTML = "";

        products.forEach(p => {
            const div = document.createElement("div");
            div.style.marginBottom = "15px";

            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.value = p;
            checkbox.addEventListener("change", sendSelections);

            const label = document.createElement("label");
            label.textContent = p;

            const opacity = createSlider(0, 1, 0.5, 0.01);
            opacity.addEventListener("input", sendSelections);

            const r = createSlider(0, 255, 128);
            const g = createSlider(0, 255, 128);
            const b = createSlider(0, 255, 128);
            r.addEventListener("input", sendSelections);
            g.addEventListener("input", sendSelections);
            b.addEventListener("input", sendSelections);

            div.appendChild(checkbox);
            div.appendChild(label);
            div.appendChild(document.createTextNode(" Opacity "));
            div.appendChild(opacity);
            div.appendChild(document.createTextNode(" R "));
            div.appendChild(r);
            div.appendChild(document.createTextNode(" G "));
            div.appendChild(g);
            div.appendChild(document.createTextNode(" B "));
            div.appendChild(b);

            productSettings[p] = { checkbox, opacity, r, g, b };
            productList.appendChild(div);
        });

        sendSelections(); // send default
    }

    function sendSelections() {
        const selected = [];
        const settings = {};

        for (const p in productSettings) {
            const s = productSettings[p];
            if (s.checkbox.checked) {
                selected.push(p);
                settings[p] = {
                    opacity: s.opacity.value,
                    r: s.r.value,
                    g: s.g.value,
                    b: s.b.value,
                };
            }
        }

        fetch("/select", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ products: selected, settings })
        });
    }

    // 🎨 Real-Time Lip Color Picker
    document.getElementById("lip-color").addEventListener("input", function () {
        const hex = this.value;
        const r = parseInt(hex.substring(1, 3), 16);
        const g = parseInt(hex.substring(3, 5), 16);
        const b = parseInt(hex.substring(5, 7), 16);

        if (productSettings["LIP"]) {
            productSettings["LIP"].r.value = r;
            productSettings["LIP"].g.value = g;
            productSettings["LIP"].b.value = b;
            productSettings["LIP"].checkbox.checked = true;
            sendSelections();
        }
    });

    // ✨ Preset Styles
    document.getElementById("preset-select").addEventListener("change", function () {
        const preset = this.value;

        const presets = {
            natural: {
                LIP: { r: 180, g: 90, b: 100, opacity: 0.4 },
                FOUNDATION: { r: 203, g: 192, b: 255, opacity: 0.2 },
                HIGHLIGHTER: { r: 255, g: 255, b: 255, opacity: 0.3 },
            },
            night: {
                LIP: { r: 200, g: 0, b: 0, opacity: 0.7 },
                EYELINER: { r: 80, g: 0, b: 0, opacity: 0.6 },
                EYESHADOW: { r: 30, g: 30, b: 80, opacity: 0.5 },
            },
            bold: {
                LIP: { r: 255, g: 0, b: 100, opacity: 0.9 },
                EYELINER: { r: 0, g: 0, b: 0, opacity: 0.8 },
                EYESHADOW: { r: 150, g: 0, b: 100, opacity: 0.6 },
                BLUSH: { r: 255, g: 50, b: 100, opacity: 0.5 },
            }
        };

        if (preset && presets[preset]) {
            const style = presets[preset];
            for (const p in style) {
                const s = style[p];
                if (productSettings[p]) {
                    productSettings[p].r.value = s.r;
                    productSettings[p].g.value = s.g;
                    productSettings[p].b.value = s.b;
                    productSettings[p].opacity.value = s.opacity;
                    productSettings[p].checkbox.checked = true;
                }
            }
            sendSelections();
        }
    });
});

/**
 * Skills tagger — transforma <input class="skills-tagger"> em um campo de tags
 * com autocomplete remoto, usando Tom Select.
 */
(function () {
    "use strict";

    function init(input) {
        // Evita inicialização dupla
        if (input.tomselect || input.dataset.tomSelectInitialized) return;

        const url = input.dataset.autocompleteUrl;
        if (!url || !window.TomSelect) return;

        // Marca como inicializado
        input.dataset.tomSelectInitialized = 'true';

        // Valor inicial vem como CSV → vira array de tags
        const initial = (input.value || "")
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean);

        new TomSelect(input, {
            create: true,                    // Permite criar novas tags
            persist: true,                   // Mantém opções criadas
            createOnBlur: true,              // Cria tag ao perder foco
            delimiter: ",",
            plugins: ["remove_button"],
            maxOptions: 50,
            valueField: "value",
            labelField: "text",
            searchField: "text",
            placeholder: input.placeholder || "Digite e pressione Enter...",
            options: initial.map((s) => ({value: s, text: s})),
            items: initial,
            load: function (query, callback) {
                if (!query.length) return callback();
                fetch(url + "?q=" + encodeURIComponent(query))
                    .then((r) => r.json())
                    .then(callback)
                    .catch(() => callback());
            },
            render: {
                option_create: function (data, escape) {
                    return '<div class="create"><i class="bi bi-plus-circle"></i> Adicionar <strong>' + escape(data.input) + '</strong></div>';
                },
                no_results: function () {
                    return '<div class="no-results">Nenhum resultado encontrado</div>';
                },
            },
        });

        // Força ocultação do input original
        input.style.cssText = 'position: absolute !important; left: -9999px !important; width: 1px !important; height: 1px !important; opacity: 0 !important;';
        input.classList.add('tomselected');
    }

    // Inicializa quando DOM estiver pronto
    function initAll() {
        document.querySelectorAll("input.skills-tagger").forEach(init);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initAll);
    } else {
        initAll();
    }
})();




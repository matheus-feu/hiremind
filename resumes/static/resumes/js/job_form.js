(function () {
    'use strict';

    let formChanged = false;
    const form = document.getElementById('jobForm');

    if (!form) return;

    // Marca formulário como alterado
    form.addEventListener('change', () => {
        formChanged = true;
    });

    // Avisa antes de sair sem salvar
    window.addEventListener('beforeunload', (e) => {
        if (formChanged) {
            e.preventDefault();
            e.returnValue = '';
        }
    });

    // Reseta flag ao submeter
    form.addEventListener('submit', () => {
        formChanged = false;
    });
})();


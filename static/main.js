import { showModal, hideModal } from './modal.js';

// Wait for DOM to load before accessing elements
document.addEventListener('DOMContentLoaded', () => {

    // const showBtn = document.getElementById('showBtn');
    const calendlyBtn = document.getElementById('calendlyBtn');
    // const hideBtn = document.getElementById('hideBtn');

    // showBtn.addEventListener('click', () => showModal('formModal'));
    calendlyBtn.addEventListener('click', calendlyRedirect);
    // hideBtn.addEventListener('click', () => hideModal('formModal'))

});

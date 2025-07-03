import { showModal, hideModal } from './modal.js';

const form = document.getElementById("contactForm");
const modal = document.getElementById('contactModal')
const closeBtn = document.getElementById("closeModalButton");

closeBtn.addEventListener("click", () => {
    modal.style.display = "none";
});

// Wait for DOM to load before accessing elements
document.addEventListener('DOMContentLoaded', () => {

    // const showBtn = document.getElementById('showBtn');
    const calendlyBtn = document.getElementById('calendlyBtn');
    // const hideBtn = document.getElementById('hideBtn');

    // showBtn.addEventListener('click', () => showModal('formModal'));
    calendlyBtn.addEventListener('click', calendlyRedirect);
    // hideBtn.addEventListener('click', () => hideModal('formModal'))

});

function closeModal() {
    modal.style.display = "none";
}

window.onclick = function (event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}
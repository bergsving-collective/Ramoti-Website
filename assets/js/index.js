const customPlanningCheckbox = document.getElementById('interestCustomPlanning');
const customPlanningField = document.getElementById('customPlanningField');
const customPlanningInput = document.getElementById('formCustomPlanning');

const toggleCustomPlanningField = () => {
    const isChecked = customPlanningCheckbox.checked;
    customPlanningField.classList.toggle('hidden', !isChecked);
    if (!isChecked) {
        customPlanningInput.value = '';
    }
};

customPlanningCheckbox.addEventListener('change', toggleCustomPlanningField);
toggleCustomPlanningField();

document.getElementById('baliForm').addEventListener('submit', (event) => {
    event.preventDefault();

    const phoneNumber = '6281239113232';

    const name = document.getElementById('formName').value;
    const contact = document.getElementById('formContact').value;
    const message = document.getElementById('formMessage').value;

    const selectedInterests = [];
    document.querySelectorAll('input[name="interest"]:checked').forEach((checkbox) => {
        selectedInterests.push(checkbox.value);
    });
    const customPlanningDetails = customPlanningInput.value.trim();
    if (customPlanningCheckbox.checked && customPlanningDetails) {
        selectedInterests.push(`Custom Planning details: ${customPlanningDetails}`);
    }
    const interestsText = selectedInterests.length > 0 ? selectedInterests.join(', ') : 'General Inquiry';

    const fullMessage = `Halo Yogi! I am interested in Ramoti Bali services.%0A%0A` +
        `*Name:* ${encodeURIComponent(name)}%0A` +
        `*Contact:* ${encodeURIComponent(contact)}%0A` +
        `*Interested in:* ${encodeURIComponent(interestsText)}%0A` +
        `*Message:* ${encodeURIComponent(message)}%0A%0A` +
        'Sent from Ramoti.com';

    const whatsappUrl = `https://api.whatsapp.com/send?phone=${phoneNumber}&text=${fullMessage}`;

    window.open(whatsappUrl, '_blank');
});

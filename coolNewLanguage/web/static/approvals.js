function handleRadioControl() {
    const approveAllRadio = document.getElementById('approveAll');
    const manualRadio = document.getElementById('manualSelection');

    if (approveAllRadio.checked) {
        // Shift all radio buttons to approve
        const allApproveRadios = document.querySelectorAll(
            'input[type="radio"][value="approve"]'
        );
        allApproveRadios.forEach(radio => { radio.checked = true });
    } else if (manualRadio.checked) {
        // Shift all radio buttons to pending
        const allPendingRadios = document.querySelectorAll(
            'input[type="radio"][value="pending"]'
        );
        allPendingRadios.forEach(radio => { radio.checked = true });
    }
}
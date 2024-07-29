function handleRadioControl() {
    const approveAllRadio = document.getElementById('approveAll');
    const rejectAllRadio = document.getElementById('rejectAll');
    const manualRadio = document.getElementById('manualSelection');

    if (approveAllRadio.checked) {
        // Shift all radio buttons to approve
        const allApproveRadios = document.querySelectorAll(
            'input[type="radio"][value="approve"]'
        );
        allApproveRadios.forEach(radio => { radio.checked = true });
    } else if (rejectAllRadio.checked) {
        // Shift all radio buttons to reject
        const allRejectRadios = document.querySelectorAll(
            'input[type="radio"][value="reject"]'
        );
        allRejectRadios.forEach(radio => { radio.checked = true });
    } else if (manualRadio.checked) {
        // Shift all radio buttons to pending
        const allPendingRadios = document.querySelectorAll(
            'input[type="radio"][value="pending"]'
        );
        allPendingRadios.forEach(radio => { radio.checked = true });
    }
}
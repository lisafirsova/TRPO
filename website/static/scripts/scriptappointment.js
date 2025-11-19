document.addEventListener('DOMContentLoaded', () => {
    const doctorsData = JSON.parse(document.getElementById("doctors-data").textContent);
    const specSelect = document.getElementById("specialty-select");
    const doctorSelect = document.getElementById("doctor-select");
    const dateTimeGrid = document.getElementById("date-time-grid");

    specSelect.addEventListener("change", () => {
        const selectedSpec = specSelect.value;
        doctorSelect.innerHTML = '<option value="">Выберите</option>';
        dateTimeGrid.innerHTML = '<p class="loading-message">Выберите врача.</p>';

        if (selectedSpec) {
            doctorsData.forEach(doc => {
                if (doc.spec_name === selectedSpec) {
                    doctorSelect.innerHTML += `<option value="${doc.doctor_id}">${doc.doctor_name}</option>`;
                }
            });
        }
    });

    doctorSelect.addEventListener("change", () => {
        const doctorId = doctorSelect.value;
        dateTimeGrid.innerHTML = '<p class="loading-message">Загрузка расписания...</p>';
        if (doctorId) {
            fetch(`/api/schedule/${doctorId}`)
                .then(response => response.json())
                .then(slots => renderSchedule(slots))
                .catch(error => {
                    console.error(error);
                    dateTimeGrid.innerHTML = '<p class="loading-message error">Не удалось загрузить расписание. Попробуйте позже.</p>';
                });
        }
    });

    function renderSchedule(slots) {
        if (slots.length === 0) {
            dateTimeGrid.innerHTML = '<p class="loading-message">На ближайшее время свободных слотов нет.</p>';
            return;
        }

        dateTimeGrid.innerHTML = '';
        const slotsByDate = slots.reduce((acc, slot) => {
            const date = slot.data_priema;
            if (!acc[date]) acc[date] = [];
            acc[date].push(slot);
            return acc;
        }, {});

        const now = new Date();

        function parseSlotDateTime(dateStr, timeStr) {
            const timeParts = (timeStr || '').split(':').map(s => parseInt(s, 10));
            let hours = timeParts[0] || 0;
            let minutes = timeParts[1] || 0;

            const iso = new Date(`${dateStr}T${String(hours).padStart(2,'0')}:${String(minutes).padStart(2,'0')}:00`);
            if (!isNaN(iso.getTime())) return iso;

            const parts = dateStr.split('.');
            if (parts.length === 3) {
                const d = parseInt(parts[0], 10);
                const m = parseInt(parts[1], 10) - 1;
                const y = parseInt(parts[2], 10);
                return new Date(y, m, d, hours, minutes, 0);
            }
            const fallback = new Date(dateStr);
            return isNaN(fallback.getTime()) ? new Date(8640000000000000) : fallback;
        }

        for (const date in slotsByDate) {
            const dateGroup = document.createElement('div');
            dateGroup.classList.add('date-group');
            dateGroup.innerHTML = `<h4 align="center">${date}</h4>`;

            const timeList = document.createElement('div');
            timeList.classList.add('time-list');

            slotsByDate[date].forEach(slot => {
                const slotDateTime = parseSlotDateTime(slot.data_priema, slot.time_priema);
                if (slotDateTime.getTime() <= now.getTime()) return;

                const timeButton = document.createElement('button');
                timeButton.type = 'button';
                timeButton.textContent = slot.time_priema;
                timeButton.classList.add('time-slot');

                if (slot.status_slot && String(slot.status_slot).toLowerCase().includes('зан')) {
                    timeButton.classList.add('booked');
                    timeButton.disabled = true;
                    timeButton.setAttribute('aria-disabled', 'true');
                } else {
                    timeButton.classList.add('available');
                    timeButton.dataset.slotId = slot.id_rasp;
                    timeButton.dataset.dateTime = `${slot.data_priema} в ${slot.time_priema}`;
                    timeButton.addEventListener('click', () => openBookingModal(slot));
                }

                timeList.appendChild(timeButton);
            });
            if (timeList.children.length === 0) continue;

            dateGroup.appendChild(timeList);
            dateTimeGrid.appendChild(dateGroup);
        }
    }

    const bookingModal = document.getElementById('booking-modal');
    const codeModal = document.getElementById('code-modal');
    const closeBtns = document.querySelectorAll('.close-modal-btn');

    function openBookingModal(slot) {
        const slotInfoDiv = document.getElementById('slot-info');
        const patientForm = document.getElementById('patient-form');
        const doctorSelect = document.getElementById('doctor-select');
        const doctorName = doctorSelect.options[doctorSelect.selectedIndex]
            ? doctorSelect.options[doctorSelect.selectedIndex].text
            : '';
        const displayDoctor = slot.doctor_name && slot.doctor_name.trim() ? slot.doctor_name : doctorName;
        slotInfoDiv.innerHTML = `
            <p><strong>Врач:</strong> ${displayDoctor}</p>
            <p><strong>Дата:</strong> ${slot.data_priema}</p>
            <p><strong>Время:</strong> ${slot.time_priema}</p>
        `;
        patientForm.dataset.slotIdToBook = slot.id_rasp;
        bookingModal.classList.add('visible');
        patientForm.querySelector('input').focus();
    }

    function closeBookingModal() {
        bookingModal.classList.remove('visible');
        document.getElementById('patient-form').reset();
    }

    function closeCodeModal() {
        codeModal.classList.remove('visible');
        document.getElementById('code-input').value = '';
    }

    closeBtns.forEach(btn => btn.addEventListener('click', () => {
        if (bookingModal.classList.contains('visible')) closeBookingModal();
        if (codeModal.classList.contains('visible')) closeCodeModal();
    }));

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            if (bookingModal.classList.contains('visible')) closeBookingModal();
            if (codeModal.classList.contains('visible')) closeCodeModal();
        }
    });
    document.getElementById('patient-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const patientForm = e.target;
        const slotId = patientForm.dataset.slotIdToBook;
        const formData = {
            slot_id: slotId,
            fio: document.getElementById('fio').value,
            dob: document.getElementById('dob').value,
            phone: document.getElementById('phone').value,
            email: document.getElementById('email').value
        };

        try {
            const resp = await fetch('/api/book', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(formData)
            });
            const result = await resp.json();

            if (resp.ok) {
                sessionStorage.setItem('bookingNotification', JSON.stringify({ type: 'success', text: 'Талон успешно оформлен.' }));
                closeBookingModal();
                openCodeModal(slotId);
            } else {
                alert(result.message);
            }
        } catch (err) {
            alert('Ошибка сети. Попробуйте позже.');
        }
    });

    function openCodeModal(slotId) {
    codeModal.classList.add('visible');
    const codeInput = document.getElementById('code-input');
    codeInput.value = '';
    codeInput.focus();

    const confirmBtn = document.getElementById('confirm-code-btn');

    confirmBtn.onclick = async () => {
        const code = codeInput.value.trim();
        if (!code) {
            codeInput.style.border = '1px solid red';
            return;
        } else {
            codeInput.style.border = '';
        }

        try {
            const resp = await fetch('/api/confirm', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({slot_id: slotId, code})
            });
            const result = await resp.json();

            if (resp.ok) {
                const btn = document.querySelector(`button.time-slot[data-slot-id="${slotId}"]`);
                if (btn) {
                    btn.classList.add('booked');
                    btn.disabled = true;
                    btn.setAttribute('aria-disabled', 'true');
                    btn.onclick = null;
                }

                if (btn) {
                    const timeList = btn.closest('.time-list');
                    if (timeList) {
                        const available = timeList.querySelector('button.time-slot:not(.booked)');
                        if (!available) {
                            const dateGroup = timeList.closest('.date-group');
                            if (dateGroup) dateGroup.remove();
                        }
                    }
                }

                closeCodeModal();
                
                sessionStorage.setItem('bookingNotification', JSON.stringify({ type: 'success', text: result.message || 'Талон успешно оформлен.' }));
                setTimeout(() => { window.location.href = '/'; }, 400);
            } else {
                codeInput.style.border = '1px solid red'; 
            }
        } catch (err) {
            console.error(err);
        }
    };
}


    const notification = sessionStorage.getItem('bookingNotification');
    if (notification) {
        const { type, text } = JSON.parse(notification);
        alert(text);
        sessionStorage.removeItem('bookingNotification');
    }
});

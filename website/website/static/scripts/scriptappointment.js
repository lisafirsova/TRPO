document.addEventListener('DOMContentLoaded', () => {
    const doctorsData = JSON.parse(document.getElementById("doctors-data").textContent);
    const specSelect = document.getElementById("specialty-select");
    const doctorSelect = document.getElementById("doctor-select");
    const dateTimeGrid = document.getElementById("date-time-grid");

    specSelect.addEventListener("change", () => {
        const selectedSpec = specSelect.value;
        dateTimeGrid.innerHTML = '';

        if (selectedSpec) {
            let options = '';
            doctorsData.forEach(doc => {
                if (doc.spec_name === selectedSpec) {
                    options += `<option value="${doc.doctor_id}">${doc.doctor_name}</option>`;
                }
            });
            
            doctorSelect.innerHTML = `<option value="any">Любой врач</option>` + options;
            doctorSelect.value = 'any';
            doctorSelect.dispatchEvent(new Event('change'));
        } else {
            doctorSelect.innerHTML = '<option value="">Выберите врача</option>';
            dateTimeGrid.innerHTML = '<p class="loading-message">Выберите специальность.</p>';
        }
    });

    doctorSelect.addEventListener("change", () => {
        const doctorId = doctorSelect.value;
        dateTimeGrid.innerHTML = '<p class="loading-message">Загрузка расписания...</p>';
        if (doctorId) {
            if (doctorId === 'any') {
                const spec = specSelect.value;
                fetch(`/api/schedule?specialty=${encodeURIComponent(spec)}`)
                    .then(response => response.json())
                    .then(slots => {
                        const freeSlots = slots.filter(s => !(s.status_slot && String(s.status_slot).toLowerCase().includes('зан')));
                        renderSchedule(freeSlots);
                    })
                    .catch(error => {
                        console.error(error);
                        dateTimeGrid.innerHTML = '<p class="loading-message error">Не удалось загрузить расписание. Попробуйте позже.</p>';
                    });
                return;
            }
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
            dateTimeGrid.innerHTML = '<p class="loading-message">Свободных талонов нет.</p>';
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

        function formatDateDisplay(dateStr) {
            const isoMatch = /^\d{4}-\d{2}-\d{2}$/.test(dateStr);
            if (isoMatch) {
                const parts = dateStr.split('-');
                return `${parts[2]}.${parts[1]}.${parts[0]}`;
            }
            return dateStr;
        }
        Object.keys(slotsByDate).sort().forEach(date => {
            const dateGroup = document.createElement('div');
            dateGroup.classList.add('date-group');
            dateGroup.innerHTML = `<h4 align="center">${formatDateDisplay(date)}</h4>`;

            const timeList = document.createElement('div');
            timeList.classList.add('time-list');
                const slotsByTime = {};
                slotsByDate[date].forEach(slot => {
                    const time = slot.time_priema || '';
                    if (!slotsByTime[time]) slotsByTime[time] = [];
                    slotsByTime[time].push(slot);
                });

                Object.keys(slotsByTime).sort().forEach(time => {
                    const group = slotsByTime[time];
                    group.sort((a, b) => {
                        const da = (a.doctor_name || '').toLowerCase();
                        const db = (b.doctor_name || '').toLowerCase();
                        return da.localeCompare(db, 'ru');
                    });

                    const futureGroup = group.filter(s => parseSlotDateTime(s.data_priema, s.time_priema).getTime() > now.getTime());
                    if (futureGroup.length === 0) return;

                    const ids = futureGroup.map(s => String(s.id_rasp));

                    const timeButton = document.createElement('button');
                    timeButton.type = 'button';
                    timeButton.textContent = time;
                    timeButton.classList.add('time-slot');
                    timeButton.dataset.slotIds = ids.join(',');
                    timeButton.dataset.dateTime = `${date} в ${time}`;

                    const hasFree = futureGroup.some(s => !(s.status_slot && String(s.status_slot).toLowerCase().includes('зан')));
                    if (!hasFree) {
                        timeButton.classList.add('booked');
                        timeButton.disabled = true;
                        timeButton.setAttribute('aria-disabled', 'true');
                    } else {
                        timeButton.classList.add('available');
                        timeButton.addEventListener('click', (e) => {
                            console.log('time-slot clicked, dataset.slotIds=', e.currentTarget.dataset.slotIds);
                            const idsList = (e.currentTarget.dataset.slotIds || '').split(',').map(x => x.trim()).filter(Boolean);
                            let chosenId = null;
                            for (const id of idsList) {
                                const slotObj = slots.find(s => String(s.id_rasp) === id);
                                if (!slotObj) continue;
                                if (!(slotObj.status_slot && String(slotObj.status_slot).toLowerCase().includes('зан'))) {
                                    chosenId = id; break;
                                }
                            }
                            if (chosenId) {
                                const slotObj = slots.find(s => String(s.id_rasp) === chosenId);
                                if (slotObj) openBookingModal(slotObj);
                            } else {
                                e.currentTarget.classList.add('booked');
                                e.currentTarget.disabled = true;
                            }
                        });
                    }

                    const slotWrapper = document.createElement('div');
                    slotWrapper.classList.add('slot-wrapper');
                    slotWrapper.appendChild(timeButton);

                    timeList.appendChild(slotWrapper);
                });

                if (timeList.children.length === 0) return;
                dateGroup.appendChild(timeList);
                dateTimeGrid.appendChild(dateGroup);
        });
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
        clearValidationErrors();
        const validation = validatePatientForm(formData);
        if (!validation.ok) {
            showValidationError(validation.field, validation.message);
            return;
        }

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
    function validatePatientForm(data) {
        const fio = (data.fio || '').trim();
        const fioRegex = /^[A-Za-zА-Яа-яЁё\-\s']+$/;
        if (!fio) return { ok: false, field: 'fio', message: 'Введите ФИО' };
        if (!fioRegex.test(fio)) return { ok: false, field: 'fio', message: 'ФИО не должно содержать цифр или специальных символов' };
        let phoneRaw = (data.phone || '').trim();
        if (!phoneRaw) return { ok: false, field: 'phone', message: 'Введите номер телефона' };
        const phoneDigits = phoneRaw.replace(/[\s()-]/g, '');
        const phoneNormalized = phoneDigits.startsWith('+') ? phoneDigits : (phoneDigits.startsWith('375') ? '+' + phoneDigits : phoneDigits);
        const phoneRegex = /^\+375\d{9}$/;
        if (!phoneRegex.test(phoneNormalized)) return { ok: false, field: 'phone', message: 'Номер должен быть в формате +375XXXXXXXXX' };

        const dobStr = data.dob;
        if (!dobStr) return { ok: false, field: 'dob', message: 'Укажите дату рождения' };
        const dob = new Date(dobStr + 'T00:00:00');
        if (isNaN(dob.getTime())) return { ok: false, field: 'dob', message: 'Неверный формат даты рождения' };
        const today = new Date();
        today.setHours(0,0,0,0);
        if (dob > today) return { ok: false, field: 'dob', message: 'Дата рождения не может быть в будущем' };
        let age = today.getFullYear() - dob.getFullYear();
        const m = today.getMonth() - dob.getMonth();
        if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) age--;
        if (age < 1) return { ok: false, field: 'dob', message: 'Пациент должен быть не младше 1 года' };
        if (age > 112) return { ok: false, field: 'dob', message: 'Пациент не может быть старше 112 лет' };

        document.getElementById('phone').value = phoneNormalized;

        return { ok: true };
    }

    function showValidationError(fieldId, message) {
        const el = document.getElementById(fieldId);
        if (el) el.style.border = '1px solid red';
        alert(message);
        if (el) el.focus();
    }

    function clearValidationErrors() {
        ['fio','phone','dob','email'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.style.border = '';
        });
    }

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
                removeSlotFromButtons(slotId);
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

    function removeSlotFromButtons(slotId) {
        const buttons = document.querySelectorAll('button.time-slot');
        buttons.forEach(btn => {
            const ids = (btn.dataset.slotIds || '').split(',').map(x => x.trim()).filter(Boolean);
            if (ids.includes(String(slotId))) {
                const newIds = ids.filter(id => id !== String(slotId));
                if (newIds.length === 0) {
                    btn.classList.add('booked');
                    btn.disabled = true;
                    btn.setAttribute('aria-disabled', 'true');
                    btn.dataset.slotIds = '';
                } else {
                    btn.dataset.slotIds = newIds.join(',');
                }
            }
        });
        document.querySelectorAll('.date-group').forEach(group => {
            const hasAvailable = group.querySelector('button.time-slot:not(.booked)');
            if (!hasAvailable) group.remove();
        });
    }


    const notification = sessionStorage.getItem('bookingNotification');
    if (notification) {
        const { type, text } = JSON.parse(notification);
        alert(text);
        sessionStorage.removeItem('bookingNotification');
    }
});

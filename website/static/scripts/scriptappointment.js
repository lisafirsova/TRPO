document.addEventListener('DOMContentLoaded', () => {
    const doctorsData = JSON.parse(document.getElementById("doctors-data").textContent);
    const specSelect = document.getElementById("specialty-select");
    const doctorSelect = document.getElementById("doctor-select");
    const dateTimeGrid = document.getElementById("date-time-grid");
//Фильтрация по специальности
    specSelect.addEventListener("change", () => {
        const selectedSpec = specSelect.value;
        doctorSelect.innerHTML = '<option value="">— Выберите —</option>';
        dateTimeGrid.innerHTML = '<p class="loading-message">Выберите врача.</p>';

        if (selectedSpec) {
            doctorsData.forEach(doc => {
                if (doc.spec_name === selectedSpec) {
                    doctorSelect.innerHTML += `<option value="${doc.doctor_id}">${doc.doctor_name}</option>`;
                }
            });
        }
    });
//Загрузка рассписания
    doctorSelect.addEventListener("change", () => {
        const doctorId = doctorSelect.value;
        dateTimeGrid.innerHTML = '<p class="loading-message">Загрузка расписания...</p>';
        if (doctorId) {
            fetch(`/api/schedule/${doctorId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Ошибка сети или сервера');
                    }
                    return response.json();
                })
                .then(slots => {
                    renderSchedule(slots);
                })
                .catch(error => {
                    console.error('Ошибка при загрузке расписания:', error);
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
            if (!acc[date]) {
                acc[date] = [];
            }
            acc[date].push(slot);
            return acc;
        }, {});
        for (const date in slotsByDate) {
            const dateGroup = document.createElement('div');
            dateGroup.classList.add('date-group');
            dateGroup.innerHTML = `<h4>${date}</h4>`;
            
            const timeList = document.createElement('div');
            timeList.classList.add('time-list');
            
            slotsByDate[date].forEach(slot => {
                const timeButton = document.createElement('button');
                timeButton.textContent = slot.time_priema;
                timeButton.classList.add('time-slot-btn');
                if (slot.status_slot === 'занят') {
                    timeButton.classList.add('booked');
                    timeButton.disabled = true;
                } else {
                    timeButton.classList.add('available');
                    timeButton.dataset.slotId = slot.id_rasp;
                    timeButton.dataset.dateTime = `${slot.data_priema} в ${slot.time_priema}`;
                    
                    // Предполагаем, что у вас есть функция openBookingModal
                    // timeButton.addEventListener('click', () => openBookingModal(slot)); 
                }
                
                timeList.appendChild(timeButton);
            });

            dateGroup.appendChild(timeList);
            dateTimeGrid.appendChild(dateGroup);
        }
    }

    function openBookingModal(slot) {
        const modal = document.getElementById('booking-modal');
        const slotInfoDiv = document.getElementById('slot-info');
        const patientForm = document.getElementById('patient-form');
        slotInfoDiv.innerHTML = `
            <p><strong>Врач:</strong> ${slot.doctor_name}</p>
            <p><strong>Дата:</strong> ${slot.data_priema}</p>
            <p><strong>Время:</strong> ${slot.time_priema}</p>
        `;
        patientForm.dataset.slotIdToBook = slot.id_rasp;
        modal.style.display = 'flex';
        document.querySelector('.close-modal-btn').onclick = closeBookingModal;
        modal.onclick = (e) => {
            if (e.target === modal) {
                closeBookingModal();
            }
        };
    }
    function closeBookingModal() {
        document.getElementById('booking-modal').style.display = 'none';
        document.getElementById('patient-form').reset();
    }
});
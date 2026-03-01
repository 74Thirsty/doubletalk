const tabs = document.querySelectorAll('.tab');
const panels = document.querySelectorAll('.panel');
const checks = document.querySelectorAll('[data-check]');
const progressText = document.querySelector('#progress-text');
const bar = document.querySelector('.bar');
const barFill = document.querySelector('#bar-fill');

function showPanel(id) {
	tabs.forEach((tab) => {
		tab.classList.toggle('is-active', tab.dataset.tab === id);
	});
	
	panels.forEach((panel) => {
		panel.classList.toggle('hidden', panel.id !== id);
	});
}

function updateProgress() {
	const done = [...checks].filter((check) => check.checked).length;
	const total = checks.length;
	const percent = total === 0 ? 0 : (done / total) * 100;
	
	progressText.textContent = `${done} / ${total} items completed`;
	bar.setAttribute('aria-valuenow', String(done));
	barFill.style.width = `${percent}%`;
}

tabs.forEach((tab) => {
	tab.addEventListener('click', () => showPanel(tab.dataset.tab));
});

checks.forEach((check) => {
	check.addEventListener('change', updateProgress);
});

updateProgress();

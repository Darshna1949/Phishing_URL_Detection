const form = document.querySelector('#analysis-form');
const result = document.querySelector('#result');

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  result.hidden = false;
  result.className = 'result loading';
  result.textContent = 'Analyzing URL...';

  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({url: document.querySelector('#url').value})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Analysis failed.');
    const confidence = (data.confidence * 100).toFixed(2);
    result.className = `result ${data.label.toLowerCase()}`;
    const modeNote = data.source === 'demo_heuristic' ? `<small>${data.message}</small>` : '';
    result.innerHTML = `<span class="result-label">${data.label === 'PHISHING' ? '⚠' : '✓'} ${data.label}</span><strong>${confidence}% confidence</strong><p>${data.label === 'PHISHING' ? 'The URL shows patterns commonly associated with phishing URLs.' : 'The URL resembles patterns learned from legitimate training examples.'}</p>${modeNote}`;
  } catch (error) {
    result.className = 'result error';
    result.textContent = error.message;
  }
});

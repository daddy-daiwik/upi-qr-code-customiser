# UPI QR Code Customiser

A 100% client-side, offline-capable Progressive Web App (PWA) for extracting UPI links from existing QR codes and generating beautiful, customized UPI QR codes with custom colors and center logos.

## Features

- **Offline-First**: Fully functional without an internet connection using Service Workers.
- **Client-Side Processing**: No backend required. Built with [PyScript](https://pyscript.net/), [jsQR](https://github.com/cozmo/jsQR), and Python's `segno` library.
- **QR Customization**: Customize the primary color, background color, and embed a center logo (e.g., GPay, PhonePe logos).
- **Fast Extraction**: Quickly reads existing UPI QR codes directly in your browser.
- **Installable**: Installable as a PWA on desktop and mobile.

## How It Works

1. **Extract**: Upload an existing UPI QR code. The app uses `jsQR` to decode the UPI URI instantly.
2. **Customize**: Tweak the colors and upload a center logo image.
3. **Generate**: The Python `segno` library, running entirely in the browser via PyScript, generates a high-quality, customized QR code on the fly.
4. **Download**: Save your newly styled UPI QR code as a PNG.

## Local Development

Since the app uses PyScript and Service Workers, it needs to be served over a local HTTP server to avoid CORS issues and allow the Service Worker to register.

1. Clone the repository:
   ```bash
   git clone https://github.com/daddy-daiwik/upi-qr-code-customiser.git
   cd upi-qr-code-customiser
   ```

2. Start a local Python server:
   ```bash
   python -m http.server 8080
   ```

3. Open your browser and navigate to `http://localhost:8080`.

## Deployment

The project is built to be deployed on static hosting platforms like Vercel or GitHub Pages.
It comes pre-configured with the HTML snippet for Vercel Web Analytics and Vercel Speed Insights.

### Deploying to Vercel
1. Import the repository into your Vercel account.
2. Since it's a static site, leave the build command and output directory empty (or set to `public` if configured).
3. Once deployed, you can enable Web Analytics and Speed Insights directly from the Vercel Dashboard.

## Built With

- HTML5 / CSS3
- [PyScript](https://pyscript.net/)
- [jsQR](https://github.com/cozmo/jsQR)
- [Segno](https://segno.readthedocs.io/en/latest/) (Python QR generation)
- [qrcode-artistic](https://github.com/heuer/qrcode-artistic) (Pillow-based QR styling)

## License

This project is open-source and available under the MIT License.

---
*Developed by [Daiwik Roy](https://github.com/daddy-daiwik)*

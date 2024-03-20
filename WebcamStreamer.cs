using UnityEngine;
using UnityEngine.UI;
using WebSocketSharp;

public class WebcamStreamer : MonoBehaviour
{
    public RawImage rawImage; // UI RawImage to display the webcam stream

    private WebCamTexture webcamTexture;
    private WebSocket ws;
    private string serverUrl = "ws://localhost:8000/ws"; // Replace with your server URL

    void Start()
    {
        // Get the list of available webcams
        WebCamDevice[] devices = WebCamTexture.devices;
        if (devices.Length > 0)
        {
            // Use the first available webcam
            webcamTexture = new WebCamTexture(devices[0].name);
            rawImage.texture = webcamTexture;
            webcamTexture.Play();
            
            // Connect to the WebSocket server
            ws = new WebSocket(serverUrl);
            ws.Connect();
        }
        else
        {
            Debug.LogError("No webcam found.");
        }
    }

    void Update()
    {
        // Send image data to the WebSocket server
        if (ws != null && ws.IsAlive && webcamTexture.isPlaying)
        {
            byte[] imageData = GetWebcamImageData();
            ws.Send(imageData);
        }
    }

    private byte[] GetWebcamImageData()
    {
        Texture2D texture = new Texture2D(webcamTexture.width, webcamTexture.height);
        texture.SetPixels(webcamTexture.GetPixels());
        texture.Apply();
        byte[] imageData = texture.EncodeToPNG();
        Destroy(texture); // Clean up memory
        return imageData;
    }

    void OnDestroy()
    {
        if (webcamTexture != null)
        {
            webcamTexture.Stop();
        }
        if (ws != null && ws.IsAlive)
        {
            ws.Close();
        }
    }
}
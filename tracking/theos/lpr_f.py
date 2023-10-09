

'''def ocr_image(image_path):
    # Load the OCR model
    model_path = " input model location"
    device = torch.device('cpu')
    model = torch.load(model_path, map_location=device)
    model = model.to(device)

    # Convert image to torch tensor and move to the device
    image = torch.tensor(image).unsqueeze(0).to(device)

    # Perform OCR inference
    with torch.no_grad():
        output = model(image)


    return output'''
import torch
from PIL import Image
import torchvision.models as models
from torchvision.transforms import ToTensor

model_path = "/home/itwatcher/tricycle_copy/tracking/TPS-ResNet-BiLSTM-Attn-Seed1111/best_accuracy.pth"
device = torch.device('cpu')

# Load the checkpoint
checkpoint = torch.load(model_path, map_location=device)

# Instantiate the model
model = models.resnet50(pretrained=False)  # Replace with the appropriate model architecture

# Load the saved state_dict into the model
model.load_state_dict(checkpoint)

# Move the model to the desired device
model = model.to(device)

# Set the model to evaluation mode
model.eval()

image_paths = ['/home/itwatcher/tricycle_copy/tracking/203.jpg']
images = [ToTensor()(Image.open(image_path)) for image_path in image_paths]

# Move images to the desired device
images = [image.to(device) for image in images]

# Perform inference
with torch.no_grad():
    outputs = model(images)

# Process the outputs as needed
print(outputs)

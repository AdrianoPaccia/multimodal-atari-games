import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.signal import convolve2d
import random
import matplotlib.pyplot as plt
from PIL import Image
import os
import yaml

class ImageNoise:
    def __init__(self, game:str, noise_types: list=[]):
        self.noise_types = noise_types
        self.game = game

        with open(os.path.join(os.path.dirname(__file__), f'config/{game}.yaml'), 'r') as f:
            self.config = yaml.safe_load(f)['images']

        try:
            self.random_images = np.load(os.path.join(os.path.dirname(__file__),f'offline_trajectories/{self.game}.npz'),
                       allow_pickle=True)['images']
        except:
             Warning('No offline trajectories stored!')

        if not set(noise_types).issubset(set(self.config['available_noises'])):
            raise ValueError("Noise types not supported")

    def get_observation(self, image):
        noise = random.choice(self.noise_types)
        return self.apply_noise(noise, image)

    def apply_noise(self, noise_type: str, image):
        img = image.copy()
        if noise_type == 'gaussian_noise':
            noisy_image = self.apply_gaussian_noise(img)
        elif noise_type == 'salt_pepper_noise':
            noisy_image = self.apply_salt_pepper_noise(img)
        elif noise_type == 'poisson_noise':
            noisy_image = self.apply_poisson_noise(img)
        elif noise_type == 'speckle_noise':
            noisy_image = self.apply_speckle_noise(img)
        elif noise_type == 'uniform_noise':
            noisy_image = self.apply_uniform_noise(img)
        elif noise_type == 'gaussian_blur':
            noisy_image = self.apply_gaussian_blur(img)
        elif noise_type == 'motion_blur':
            noisy_image = self.apply_gaussian_blur(img)
        elif noise_type == 'quantization_noise':
            noisy_image = self.apply_quantization_noise(img)
        elif noise_type == 'background_noise':
            noisy_image = self.apply_background_noise(img)
        elif noise_type == 'confounders_noise':
            noisy_image = self.apply_confounders_noise(img)
        elif noise_type == 'random_obs':
            noisy_image = self.get_random_observation()
        elif noise_type == 'nonoise':
            noisy_image = img
        else:
            raise ValueError(f"Unsupported noise type: {noise_type}")
        return noisy_image

    def apply_random_noise(self, image):
        noise_type = random.choice(list(self.noise_types))
        return self.apply_noise(noise_type, image)

    def apply_all_noises(self, image):
        noisy_images = []
        for noise_type in self.noise_types:
            noisy_images.append(self.apply_noise(noise_type, image))
        return noisy_images, self.noise_types

    # all implemented noises

    def apply_gaussian_noise(self, image):
        mean = self.config['gaussian_noise']['mu']
        stddev = self.config['gaussian_noise']['std']
        noise = np.random.normal(mean, stddev, image.shape).astype(np.uint8)
        noisy_image = np.clip(image.astype(np.int16) + noise.astype(np.int16), 0, 255).astype(np.uint8)
        return noisy_image

    def apply_salt_pepper_noise(self, image):
        ratio = self.config['salt_pepper_noise']['ratio']
        salt_pepper = np.random.rand(*image.shape)
        noisy_image = np.copy(image)
        noisy_image[salt_pepper < ratio] = 0
        noisy_image[salt_pepper > 1 - ratio] = 255
        return noisy_image

    def apply_poisson_noise(self, image):
        noisy_image = np.random.poisson(image)
        return np.clip(noisy_image, 0, 255).astype(np.uint8)

    def apply_speckle_noise(self, image):
        noise = np.random.normal(0, 1, size=image.shape)
        mean = self.config['speckle_noise']['mean']
        std = self.config['speckle_noise']['std']
        noisy_image = np.random.normal(mean, std, image.shape) * image + image
        return np.clip(noisy_image, 0, 255).astype(np.uint8)

    def apply_uniform_noise(self, image):
        min_val = self.config['uniform_noise']['min_val']
        max_val = self.config['uniform_noise']['max_val']
        noise = np.random.uniform(min_val, max_val, size=image.shape)
        noisy_image = np.clip(image + noise, 0, 255).astype(np.uint8)
        return noisy_image

    def apply_gaussian_blur(self, image):
        sigma = self.config['gaussian_blur']['sigma']
        noisy_image = gaussian_filter(image, sigma=sigma)
        return np.clip(noisy_image, 0, 255).astype(np.uint8)

    def apply_motion_blur(self, image):
        kernel_size = self.config['motion_blur']['kernel_size']
        angle = self.config['motion_blur']['angle']
        kernel = self._motion_blur_kernel(kernel_size, angle)
        noisy_image = convolve2d(image, kernel, mode='same', boundary='wrap')
        return np.clip(noisy_image, 0, 255).astype(np.uint8)

    def apply_quantization_noise(self, image):
        bits = self.config['quantization_noise']['bits']
        noise = np.random.uniform(0, 1, size=image.shape)
        levels = 2 ** bits - 1
        noisy_image = (image / 255 * levels) / levels * 255
        return np.clip(noisy_image, 0, 255).astype(np.uint8)

    def apply_confounders_noise(self, image):
        noisy_image = image.copy()
        max_patch_size = self.config['confounders_noise']['max_size']
        min_patch_size = self.config['confounders_noise']['min_size']
        max_num_patches = self.config['confounders_noise']['max_num_patches']
        n = random.randint(1, max_num_patches)
        height, width, _ = image.shape

        for _ in range(n):
            side_1 = random.randint(min_patch_size, max_patch_size)
            side_2 = random.randint(min_patch_size, max_patch_size)
            x = random.randint(0, width - side_1)
            y = random.randint(0, height - side_2)
            for i in range(3):
                noisy_image[y:y + side_1, x:x + side_2, i] = random.uniform(0, 225)
        return noisy_image

    def get_random_observation(self):
        i_rand = random.randint(0, self.random_images.shape[0] - 1)
        return self.random_images[i_rand]

    def apply_background_noise(self, original_image):
        img_path = os.path.join(os.path.dirname(__file__), self.config['img_path'])
        # randomly get an image as background
        image_files = os.listdir(img_path)
        image_files = [file for file in image_files if file.endswith(('.jpg', '.jpeg', '.png'))]
        random_image = random.choice(image_files)
        bg_image = Image.open(os.path.join(img_path, random_image))
        bg_image = bg_image.resize(original_image.shape[:2])
        background_image = np.array(bg_image)

        # background_image = np.random.randint(0, 256, original_image.shape, dtype=np.uint8)
        original_image = np.array(original_image.copy()).astype(np.uint8)

        if original_image.shape != background_image.shape:
            raise ValueError("Original and disturbing images must have the same size")

        gray = np.dot(original_image[..., :3], [0.2989, 0.5870, 0.1140])

        # Apply Otsu's thresholding
        threshold = np.mean(gray)+0.1
        mask = (gray < threshold).astype(np.uint8) * 255

        # Create the masks
        foreground_mask = np.stack([mask] * 3, axis=-1)
        background_mask = 255 - foreground_mask
        foreground_mask = (foreground_mask.astype(np.float32) / 255.0)
        background_mask = (background_mask.astype(np.float32) / 255.0)

        # Combine the foreground and background
        composite_image = (background_mask * background_image) + (foreground_mask * original_image)
        composite_image = np.clip(composite_image, 0, 255).astype(np.uint8)

        return composite_image

    def _motion_blur_kernel(self, size, angle):
        kernel = np.zeros((size, size))
        kernel[int((size - 1) / 2), :] = np.sin(np.deg2rad(angle))
        kernel[int((size - 1) / 2), int((size - 1) / 2)] = np.cos(np.deg2rad(angle))
        kernel /= np.sum(kernel)
        return kernel

    def render_images(self, image_list, noise_types):
        n = len(image_list)
        fig, axes = plt.subplots(1, n, figsize=(10, 5))  # Create a figure with two subplots
        for i in range(n):
            axes[i].imshow(image_list[i])
            axes[i].axis('off')
            axes[i].set_title(f'{noise_types[i]}')
        plt.show()


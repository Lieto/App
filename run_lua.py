import os
import subprocess

def run_nn(style_image, original_image):

    os.chdir('/home/ubuntu/Deepstyle/neural_style')

    args = ['th',
            'neural_style.lua',
            '-style_image',
            style_image,
            '-content_image',
            original_image,
            ]
    result = subprocess.check_output()
    print(result)

if __name__ == '__main__':

    style_image = '/home/ubuntu/DeepStyle/neural_style/picasso.jpg'
    original_image = '/home/ubuntu/App/uploads/m_test.jpg'
    run_nn(style_image, original_image)

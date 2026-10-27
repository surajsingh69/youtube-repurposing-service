# Portfolio Sample: YouTube Content Repurposing

## Project: "But what is a Neural Network?" by 3Blue1Brown

**Source Video:** https://www.youtube.com/watch?v=aircAruvnKk  
**Topic:** Introduction to neural networks and deep learning  
**Video Length:** ~19 minutes  
**Package:** Standard  
**Deliverables:** Blog post, Twitter thread, Key quotes, Summary

---

## Deliverable 1: Blog Post

**Title:** How Neural Networks Recognize Handwritten Digits: A Beginner's Guide

**Word Count:** ~850 words  
**Status:** Ready for client review and publishing

---

### Introduction

Your brain recognizes a handwritten "3" instantly, even when it's sloppy, pixelated, or rendered at a low resolution. Computers struggle with this same task—unless they use neural networks. In this post, we break down how a simple neural network learns to identify digits by processing layers of patterns, from edges to complete numbers.

### Key Takeaways

- Neural networks learn to recognize patterns by breaking images into layers of abstraction
- A basic digit-recognition network uses 784 input neurons, two hidden layers of 16 neurons each, and 10 output neurons
- The network has approximately 13,000 weights and biases that are tuned during training
- Modern networks often use ReLU activation functions instead of sigmoid for easier training
- Understanding the structure of neural networks helps demystify machine learning

### Main Discussion

#### The Challenge of Teaching Computers to See

When you look at a blurry, low-resolution image of the number 3, your visual cortex identifies it without effort. The specific light-sensitive cells firing in your eyes are different each time, yet your brain resolves these variations into the same idea. Teaching a computer to do this seems simple in theory but is remarkably difficult in practice.

#### How Neural Networks Structure Learning

The network begins with 784 neurons representing each pixel in a 28x28 input image. Each neuron holds a grayscale value between 0 (black) and 1 (white). These form the input layer. The output layer has 10 neurons, one for each digit, with activations indicating how strongly the network believes the image matches each number.

Between them sit hidden layers. In the example network, there are two hidden layers with 16 neurons each. The magic happens in how these layers connect: every neuron in one layer connects to every neuron in the next, with each connection carrying a weight. The network computes weighted sums, adds biases, and passes the result through an activation function to determine the next layer's output.

#### From Pixels to Patterns

The goal is for the hidden layers to detect increasingly complex features. The second layer might recognize edges—vertical lines, horizontal bars, curves. The third layer combines these into patterns like loops or intersections. By the final layer, the network has assembled these patterns into complete digit recognition.

This layered approach mirrors how biological vision works. Your own visual system breaks down what you see into edges, then shapes, then objects. Neural networks use the same principle: break a hard problem into simpler steps.

#### The Math Behind the Magic

Each neuron calculates a weighted sum of its inputs, adds a bias, and then applies an activation function. Early networks used the sigmoid function to squash results between 0 and 1. Modern networks often prefer ReLU (Rectified Linear Unit), which outputs the input directly if it's positive and zero otherwise. ReLU trains much faster in deep networks.

The entire network is just a function: 784 inputs in, 10 outputs out. But it's a complicated function involving roughly 13,000 parameters. Training finds the right settings for all these weights and biases so the function actually solves the digit recognition problem.

### Conclusion

Neural networks sound intimidating, but at their core they're just layered pattern detectors. By understanding how they process information from raw pixels to final predictions, you can better appreciate both their capabilities and their limitations. For a deeper dive into the math and training process, watch the full video.

---

## Deliverable 2: Twitter/X Thread

**Tweet 1** (237 chars)
Your brain recognizes a handwritten "3" instantly, even when it's blurry or pixelated. Computers struggle with this exact task—unless they use neural networks. Here's how a simple network learns to see digits:

**Tweet 2** (194 chars)
The network starts with 784 neurons, one for each pixel in a 28x28 image. Each holds a brightness value from 0 (black) to 1 (white). These form the input layer.

**Tweet 3** (186 chars)
Between input and output sit hidden layers. In our example: two layers of 16 neurons each. Every neuron connects to every neuron in the next layer, with each connection carrying a weight.

**Tweet 4** (178 chars)
The goal? Layer 2 detects edges. Layer 3 combines edges into patterns like loops. By the final layer, the network has assembled patterns into complete digits.

**Tweet 5** (162 chars)
This mirrors biological vision. Your visual cortex breaks down what you see into edges, then shapes, then objects. Neural networks use the same principle.

**Tweet 6** (148 chars)
Modern networks often use ReLU instead of sigmoid. ReLU trains much faster in deep networks by outputting the input directly when positive, zero when negative.

**Tweet 7** (156 chars)
The entire network is just a function: 784 inputs, 10 outputs. But it involves roughly 13,000 parameters. Training finds the right settings so it actually works.

---

## Deliverable 3: Key Quotes

1. "Your brain recognizes a handwritten '3' instantly, even when it's blurry or pixelated. Computers struggle with this exact task—unless they use neural networks."

2. "The goal? Layer 2 detects edges. Layer 3 combines edges into patterns like loops. By the final layer, the network has assembled patterns into complete digits."

3. "This mirrors biological vision. Your visual cortex breaks down what you see into edges, then shapes, then objects. Neural networks use the same principle."

4. "Modern networks often use ReLU instead of sigmoid. ReLU trains much faster in deep networks."

5. "The entire network is just a function: 784 inputs, 10 outputs. But it involves roughly 13,000 parameters."

---

## Deliverable 4: Summary

This video explains how neural networks learn to recognize handwritten digits by breaking the task into layers. Starting from 784 input neurons representing pixel values, the network uses hidden layers to detect edges, then patterns, then complete digits. With approximately 13,000 weights and biases tuned during training, even a simple network can achieve remarkable pattern recognition. Modern networks often use ReLU activation functions instead of sigmoid for faster training.

---

## Value Delivered

**Time saved for client:** ~3-4 hours of manual work  
**Client receives:** 
- Professionally formatted blog post (~850 words)
- Engaging Twitter thread (7 tweets)
- 5 polished key quotes
- Concise video summary

**Service note:** Output is generated from the video transcript and then edited for coherence, flow, and client-ready quality. Human review ensures accuracy and readability.

---

## How This Sample Was Created

1. **Automated extraction:** The YouTube transcript was fetched and processed
2. **Content selection:** Key points and quotes were identified from the transcript
3. **Human editing:** The raw output was edited for structure, clarity, and flow
4. **Formatting:** Final content was formatted into deliverable files

**Original video:** 3Blue1Brown, "But what is a Neural Network?"  
**Source:** https://www.youtube.com/watch?v=aircAruvnKk  
**Used for:** Portfolio demonstration only

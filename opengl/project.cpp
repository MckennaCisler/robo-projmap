#include <Python.h>
#include <numpy/arrayobject.h>
#include <stdlib.h>

#include <GL/glew.h>

#include <GLFW/glfw3.h>

#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include "common/shader.hpp"

#include <time.h>
using namespace glm;

/**
 * Much of this file is adapted from the following tutorials:
 * http://www.opengl-tutorial.org/intermediate-tutorials/billboards-particles/particles-instancing/
 * https://www.opengl-tutorial.org/intermediate-tutorials/tutorial-9-vbo-indexing/
 */

#define MAX_INPUT_RES 1920*1080
#define XYDC_MAX_SIZE 6*MAX_INPUT_RES
#define INDICES_MAX_SIZE 3*2*MAX_INPUT_RES

#define DEFAULT_PROJ_WIDTH      1366
#define DEFAULT_PROJ_HEIGHT     768

#define DEFAULT_INPUT_WIDTH     1920
#define DEFAULT_INPUT_HEIGHT    1080

GLFWwindow* window;
GLuint VertexArrayID;
GLuint vertexbuffer;
GLuint programID;
GLint MatrixID;
glm::mat4 MVP;
GLuint indexbuffer;
static unsigned int g_indices_data[INDICES_MAX_SIZE];

void generate_indices(int height, int width, unsigned int indices[]);

/**
 * Takes in (np.ndarray projector matrix, output monitor index). 
 * The projector matrix must be 4x4, and output monitor can be negative for windowed mode.
 * Returns True on success, False otherwise
 */
PyObject *start(PyObject *self, PyObject *args) {
    int proj_width = DEFAULT_PROJ_WIDTH;
    int proj_height = DEFAULT_PROJ_HEIGHT;
    int input_width = DEFAULT_INPUT_WIDTH;
    int input_height = DEFAULT_INPUT_HEIGHT;

    // Extract Python args 

    // read args
    PyObject *arg_mvp = NULL;
    PyObject *arr_mvp = NULL;
    int monitor_index;

    if (!PyArg_ParseTuple(args, "Oi", &arg_mvp, &monitor_index)) {
        Py_RETURN_NONE;
    }

    arr_mvp = PyArray_FROM_OTF(arg_mvp, NPY_FLOAT32, NPY_ARRAY_IN_ARRAY);

    int mvp_size = PyArray_Size(arr_mvp);
    if (mvp_size != 16) {
            fprintf(stderr, "Invalid size for MVP matrix\n");
            Py_RETURN_NONE;
    }

    float *mvp_data = (float*) PyArray_DATA(arr_mvp);

    // Initialise GLFW
    if( !glfwInit() ) {
        fprintf( stderr, "Failed to initialize GLFW\n" );
        Py_RETURN_FALSE;
    }

    glfwWindowHint(GLFW_SAMPLES, 4);
    glfwWindowHint(GLFW_RESIZABLE,GL_FALSE);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE); // To make MacOS happy; should not be needed
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    // Open a window and create its OpenGL context
    window = glfwCreateWindow(proj_width, proj_height, "Projector View", NULL, NULL);
    if( window == NULL ) {
        fprintf( stderr, "Failed to open GLFW window. If you have an Intel GPU, they are not 3.3 compatible. Try the 2.1 version of the tutorials.\n" );
        glfwTerminate();
        Py_RETURN_FALSE;
    }
    glfwMakeContextCurrent(window);

    // Set the window to be fullscreened in the given monitor
    if (monitor_index >= 0) {
        int count;
        GLFWmonitor** monitors = glfwGetMonitors(&count);
        if (monitor_index >= count) {
            fprintf(stderr, "Not enough monitors (%d) to project to monitor at index %d\n", count, monitor_index);
            Py_RETURN_FALSE;
        }
        glfwSetWindowMonitor(window, monitors[monitor_index], 0, 0, proj_width, proj_height, GLFW_DONT_CARE);
    }

    // Initialize GLEW
    glewExperimental = true;
    if (glewInit() != GLEW_OK) {
        fprintf(stderr, "Failed to initialize GLEW\n");
        glfwTerminate();
		Py_RETURN_FALSE;
    }

    // Ensure we can capture the escape key being pressed below
    glfwSetInputMode(window, GLFW_STICKY_KEYS, GL_TRUE);

    // Dark blue background
    glClearColor(0.0f, 0.0f, 0.4f, 0.0f);

    // Setup vertex arrays
    glGenVertexArrays(1, &VertexArrayID);
    glBindVertexArray(VertexArrayID);

    // Create and compile our GLSL program from the shaders
    programID = LoadShaders( "shader.vert", "shader.frag" );

    // Get a handle for our "MVP" uniform
    MatrixID = glGetUniformLocation(programID, "MVP");

    // Copy input python data in
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            MVP[i][j] = *(mvp_data + i*4 + j);
        }
    }

    // Generate a buffer for the vertices (XYD points)
    glGenBuffers(1, &vertexbuffer);
    glBindBuffer(GL_ARRAY_BUFFER, vertexbuffer);
    glBufferData(GL_ARRAY_BUFFER, XYDC_MAX_SIZE, NULL, GL_DYNAMIC_DRAW);

    // Populate the indices array
    generate_indices(input_width, input_height, g_indices_data);

    // Generate a buffer for the indices of the triangle points
    glGenBuffers(1, &indexbuffer);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, indexbuffer);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, INDICES_MAX_SIZE, g_indices_data, GL_STATIC_DRAW);

    Py_RETURN_TRUE;
}

void generate_indices(int height, int width, unsigned int indices[]) {
    // TODO
    indices[0] = 3;
    indices[1] = 0;
    indices[2] = 4;
    indices[3] = 0;
    indices[4] = 1;
    indices[5] = 2;
    indices[6] = 1;
    indices[7] = 5;
    indices[8] = 6;
}

/**
 * Takes in (np.ndarray xydc). 
 * xydc should contain N words of 6 values: (x*d, y*d, d, r, g, b) 
 * where N is the number of pixels, x, y are the pixel locations.
 * Returns true when the window was closed or None on error.
 */
PyObject *draw_frame(PyObject *self, PyObject *args) {
    // read args
    PyObject *arg_xydc = NULL;
    PyObject *arr_xydc = NULL;

    if (!PyArg_ParseTuple(args, "O", &arg_xydc)) {
        Py_RETURN_NONE;
    }

    arr_xydc = PyArray_FROM_OTF(arg_xydc, NPY_FLOAT32, NPY_ARRAY_IN_ARRAY);

    int xydc_size = PyArray_Size(arr_xydc);
    if (xydc_size > XYDC_MAX_SIZE) {
            fprintf(stderr, "Invalid input sizes to draw_frame\n");
            Py_RETURN_NONE;
    }

    GLfloat *xydc_data = (GLfloat*) PyArray_DATA(arr_xydc);

    // update data in buffers (reallocate the buffer objects beforehand for speed)
    // (see https://www.khronos.org/opengl/wiki/Buffer_Object_Streaming#Buffer_re-specification)
    // glBufferData(GL_ARRAY_BUFFER, XYDC_MAX_SIZE, NULL, GL_DYNAMIC_DRAW);
    glBufferSubData(GL_ARRAY_BUFFER, 0, xydc_size * sizeof(GLfloat), xydc_data);

    // reset color
    glClear(GL_COLOR_BUFFER_BIT);

    // Use our shader (the camera->projector conversion matrix and the color attribute adder)
    glUseProgram(programID);
    glUniformMatrix4fv(MatrixID, 1, GL_FALSE, &MVP[0][0]);

    // connect the xyz in first part of the buffer to the shader attribute
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(
            0,                  // attribute 0. No particular reason for 0, but must match the layout in the shader.
            3,                  // size (3-space)
            GL_FLOAT,           // type
            GL_FALSE,           // normalized?
            6*sizeof(GLfloat),  // stride
            (void*)0            // array buffer offset
    );

    // connect the color to the input color attribute of the vertex shader
    glEnableVertexAttribArray(1);
    glVertexAttribPointer(
            1,
            3,                                      // size (RGB)
            GL_FLOAT,
            GL_FALSE,                               // normalized?
            6*sizeof(GLfloat),                      // stride
            (const GLvoid*)(3 * sizeof(GLfloat))    // after xyd coordinates
    );

    // Draw the triangles using the vertex indices in the indices data
    glDrawElements(
        GL_TRIANGLES,               // mode
        INDICES_MAX_SIZE,           // count
        GL_UNSIGNED_INT,            // type
        (void*)0                    // element array buffer offset
    );

    glDisableVertexAttribArray(0);
    glDisableVertexAttribArray(1);

    // Swap buffers
    glfwSwapBuffers(window);

    // Check for exit keypresses
    glfwPollEvents();
	if (glfwGetKey(window, GLFW_KEY_ESCAPE ) != GLFW_PRESS && glfwWindowShouldClose(window) == 0) {
		Py_RETURN_FALSE;
	} else {
		Py_RETURN_TRUE;
	}
}

/**
 * Stops rendering
 */
PyObject *stop(PyObject *self, PyObject *args) {
    glfwTerminate();
	Py_RETURN_NONE;
}

static PyMethodDef ProjectMethods[] = {
	{"start",  start, METH_VARARGS, "Starts the projector display at the given resolution, using the given camera->projector conversion matrix"},
	{"draw_frame",  draw_frame, METH_VARARGS, "Transforms the given frame and corresponding triangle indices into a mesh which is then projected and displayed"},
	{"stop",  stop, METH_NOARGS, "Stops the projector display"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};


static struct PyModuleDef projectmodule = {
    PyModuleDef_HEAD_INIT,
    "project",   /* name of module */
    "basic doc string", /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    ProjectMethods
};


PyMODINIT_FUNC PyInit_project(void)
{
    import_array();
    return PyModule_Create(&projectmodule);
}

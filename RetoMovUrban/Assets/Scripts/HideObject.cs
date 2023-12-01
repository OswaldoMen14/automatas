using System.Collections;
using System.Collections.Generic;
using UnityEngine;
// Code made by Alan Hernández and Oswaldo Mendizábal with the help of Octavio Navarro and Gil Echeverría
// 30/11/2023

public class HideObject : MonoBehaviour
{
    private bool objectToggle = true;
    public GameObject objectToHide;
    // Start is called before the first frame update
    void Start()
    {
        ToggleObject();
    }

    // Public method to toggle the visibility of the object
    public void ToggleObject()
    {
        // Invert the boolean value to toggle between hiding and showing
        
        objectToggle = !objectToggle;

        // Set the active state of the referenced object based on the boolean value
        objectToHide.SetActive(objectToggle);
    }
}

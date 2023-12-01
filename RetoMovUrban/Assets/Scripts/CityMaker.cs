using System.Collections;
using System.Collections.Generic;
using UnityEngine;

// Code made by Alan Hernández and Oswaldo Mendizábal with the help of Octavio Navarro and Gil Echeverría
// 30/11/2023

public class CityMaker : MonoBehaviour
{
    [SerializeField] TextAsset layout;          // Input layout file
    [SerializeField] GameObject roadPrefab;     // Prefab for road tiles
    [SerializeField] GameObject[] buildingPrefab; // Array of building prefabs
    [SerializeField] int tileSize;               // Size of each tile

    void Start()
    {
        MakeTiles(layout.text);  // Call the MakeTiles function with the content of the layout file
    }

    void Update()
    {
        // Update function (currently empty)
    }

    void MakeTiles(string tiles)
    {
        int x = 0;
        int y = tiles.Split('\n').Length - 1; // Calculate the number of rows

        Vector3 position;
        GameObject tile;

        for (int i = 0; i < tiles.Length; i++)
        {
            if (tiles[i] == '>' || tiles[i] == '<')
            {
                // Create a road tile facing right or left
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.identity);
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == 'v' || tiles[i] == '^')
            {
                // Create a road tile facing down or up
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.Euler(0, 90, 0));
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == 's')
            {
                // Create a road tile with the default orientation
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.identity);
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == 'S')
            {
                // Create a road tile facing right or left with a rotated orientation
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.Euler(0, 90, 0));
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == 'D')
            {
                // Create a building tile with a random building prefab and a red color
                position = new Vector3(x * tileSize, 0, y * tileSize);
                var randomBuilding = Random.Range(0, buildingPrefab.Length);
                tile = Instantiate(buildingPrefab[randomBuilding], position, Quaternion.Euler(0, 90, 0));
                tile.GetComponent<Renderer>().materials[0].color = Color.red;
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == '#')
            {
                // Create a building tile with a random building prefab and a scaled y-axis
                position = new Vector3(x * tileSize, 0, y * tileSize);
                var randomBuilding = Random.Range(0, buildingPrefab.Length);
                tile = Instantiate(buildingPrefab[randomBuilding], position, Quaternion.identity);
                tile.transform.localScale = new Vector3(1, Random.Range(0.5f, 2f), 1);
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == '\n')
            {
                // Move to the next row
                x = 0;
                y -= 1;
            }
        }
    }
}

// TC2008B. Sistemas Multiagentes y Gráficas Computacionales
// C# client to interact with Python. Based on the code provided by Sergio Ruiz.
// Octavio Navarro. October 2023
// Code made by Alan Hernández and Oswaldo Mendizábal with the help of Octavio Navarro and Gil Echeverría
// 30/11/2023

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

[Serializable]
public class AgentData
{
    /*
    The AgentData class is used to store the data of each agent.
    
    Attributes:
        id (string): The id of the agent.
        x (float): The x coordinate of the agent.
        y (float): The y coordinate of the agent.
        z (float): The z coordinate of the agent.
    */
    public string id;
    public float x, y, z;
    public string state;

    public AgentData(string id, float x, float y, float z, string state)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
        this.state = state;

    }

}

[Serializable]
public class TrafficLightData
{
    // The TrafficLightData class is used to store the data of each traffic light.
    // Attributes:
    //   id (string): The id of the traffic light.
    //   x (float): The x coordinate of the traffic light.
    //   y (float): The y coordinate of the traffic light.
    //   z (float): The z coordinate of the traffic light.
    //   light (bool): The state of the traffic light (true for green, false for red).
    //   type (string): The type of the traffic light.
    public string id;
    public float x, y, z;
    public bool light;
    public string type;


    public TrafficLightData(string id, float x, float y, float z, bool light, string type)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
        this.light = light;
        this.type = type;
    }
}



[Serializable]
public class AgentsData
{
    /*
    The AgentsData class is used to store the data of all the agents.

    Attributes:
        positions (list): A list of AgentData objects.
    */
    public List<AgentData> positions;

    public AgentsData() => this.positions = new List<AgentData>();
}

[Serializable]
public class TrafficLightsData
{
    public List<TrafficLightData> positions;

    public TrafficLightsData() => this.positions= new List<TrafficLightData>();
}



public class AgentController : MonoBehaviour
{
        // URL endpoints for communication with the server

    string serverUrl = "http://localhost:8585";
    string getAgentsEndpoint = "/getAgents";
    string getTrafficLightEndpoint = "/getTrafficLights";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";
    AgentsData agentsData;
    TrafficLightsData trafficLightsData;
    Dictionary<string, GameObject> agents;

    Dictionary<string, Vector3> prevPositions, currPositions;

    bool updated = false;

    public GameObject[] agentPrefab;
    public GameObject trafficLightPrefab;
    public float timeToUpdate = 5.0f;
    private float timer, dt; 
    [SerializeField] int tileSize;
    [SerializeField] int timegenerate;

    [SerializeField] string file;

    void Start()
    {
        // Initialize data structures and start the communication with the server

        agentsData = new AgentsData();
        trafficLightsData = new TrafficLightsData();

        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();

        agents = new Dictionary<string, GameObject>();



        
        timer = timeToUpdate;

        StartCoroutine(SendConfiguration());
    }

    private void Update() 
    {
     // Update timer and check if it's time to fetch new simulation data

        if(timer < 0)
        {
            timer = timeToUpdate;
            updated = false;
            StartCoroutine(UpdateSimulation());
        }

        if (updated)
        {
            timer -= Time.deltaTime;
            dt = 1.0f - (timer / timeToUpdate);

        }
    }
 
    IEnumerator UpdateSimulation()
    {
        // Fetch updated simulation data from the server

        UnityWebRequest www = UnityWebRequest.Get(serverUrl + updateEndpoint);
        yield return www.SendWebRequest();


 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            // Update agent and traffic light data
            StartCoroutine(GetAgentsData());
            StartCoroutine(GetTrafficLight());
        }
    }

    IEnumerator SendConfiguration()
    {
        // Send initial configuration to the server
        WWWForm form = new WWWForm();
        form.AddField("timegenerate", timegenerate);
        form.AddField("file", file);



        

        UnityWebRequest www = UnityWebRequest.Post(serverUrl + sendConfigEndpoint, form);
        www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            Debug.Log("Configuration upload complete!");
            Debug.Log("Getting Agents positions");

            // Fetch initial agent and traffic light data
            StartCoroutine(GetAgentsData());
            StartCoroutine(GetTrafficLight());
        }
    }

    IEnumerator GetAgentsData() 
    {
        // Fetch agent data from the server
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getAgentsEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            // Parse and update agent positions
            agentsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            foreach(AgentData agent in agentsData.positions)
            {
                Vector3 newAgentPosition = new Vector3(agent.x, agent.y, agent.z * tileSize);

                    if(!agents.ContainsKey(agent.id))
                    {
                        // Instantiate new agent if it doesn't exist
                        prevPositions[agent.id] = newAgentPosition;
                        agents[agent.id] = Instantiate(agentPrefab[UnityEngine.Random.Range(0,agentPrefab.Length)], new Vector3(0,0,0), Quaternion.identity);
                        Apply_Transform applyTransform = agents[agent.id].GetComponent<Apply_Transform>();
                        applyTransform.SetNewPos(newAgentPosition);
                        applyTransform.SetNewPos(newAgentPosition);
                        applyTransform.moveTime = timeToUpdate;
                    }
                    // Handle destruction of agents in intermediate state
                    else if(agent.state == "intermediate"){
                        Debug.Log("wheels destroyed of the car " + agent.id);
                        Apply_Transform applyTransform = agents[agent.id].GetComponent<Apply_Transform>();
                        applyTransform.DestroyLlantas();
                        Destroy(agents[agent.id]);
                        Debug.Log("Agent " + agent.id + " died");
                        agents.Remove(agent.id); 
                        prevPositions.Remove(agent.id);
                        currPositions.Remove(agent.id);
                    }
                    else
                    {
                        Apply_Transform applyTransform = agents[agent.id].GetComponent<Apply_Transform>();
                        applyTransform.SetNewPos(newAgentPosition);
                        
                    }
            }

            updated = true;
        }
    }



    IEnumerator GetTrafficLight()
    {
       // Fetch traffic light data from the server
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getTrafficLightEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            // Parse and update traffic light positions
            trafficLightsData = JsonUtility.FromJson<TrafficLightsData>(www.downloadHandler.text);

            foreach (TrafficLightData trafficLight in trafficLightsData.positions)
            {

                Vector3 newTrafficLightPosition = new Vector3(trafficLight.x, trafficLight.y, trafficLight.z * tileSize);

                if (!agents.ContainsKey(trafficLight.id))
                {   // Instantiate new traffic light if it doesn't exist
                    if(trafficLight.type == "s")
                    {
                        
                        prevPositions[trafficLight.id] = newTrafficLightPosition;
                        agents[trafficLight.id] = Instantiate(trafficLightPrefab, newTrafficLightPosition, Quaternion.identity);
                        Debug.Log("Semaphore " + trafficLight.id + " created");
                    }
                        
                    else if(trafficLight.type == "S")
                    {
                        prevPositions[trafficLight.id] = newTrafficLightPosition;
                        agents[trafficLight.id] = Instantiate(trafficLightPrefab, newTrafficLightPosition, Quaternion.Euler(0, 90, 0));
                        Debug.Log("Semaphore " + trafficLight.id + " created");
                    }
                    else if(trafficLight.type == "X")
                    {
                        prevPositions[trafficLight.id] = newTrafficLightPosition;
                        agents[trafficLight.id] = Instantiate(trafficLightPrefab, newTrafficLightPosition, Quaternion.Euler(0, -90, 0));
                        Debug.Log("Semaphore " + trafficLight.id + " created");
                    }
                    else
                    {
                        prevPositions[trafficLight.id] = newTrafficLightPosition;
                        agents[trafficLight.id] = Instantiate(trafficLightPrefab, newTrafficLightPosition, Quaternion.Euler(0, 180, 0));
                        Debug.Log("Semaphore " + trafficLight.id + " created"+ "with type" + trafficLight.type);
                    }
                    
                    //updates light component 
                    if (trafficLight.light)
                        agents[trafficLight.id].GetComponent<Light>().color = Color.green;
                    else
                        agents[trafficLight.id].GetComponent<Light>().color = Color.red;
                }
                else
                {
                    // Update state of existing traffic lights
                    if(trafficLight.light)
                        
                        agents[trafficLight.id].GetComponent<Light>().color = Color.green;
                    else
                        agents[trafficLight.id].GetComponent<Light>().color = Color.red;
                }
            }

            updated = true;
        }
    }
}


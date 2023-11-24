/*
simulacion de movimiento de un auto, con la generacion de las llantas
usando matrices de transformacion
*/

using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Apply_Transform : MonoBehaviour
{
    [Header("Interpolation")]
    [SerializeField] Vector3 startPos;
    [SerializeField] Vector3 stopPos;
    [SerializeField] float moveTime;


    [SerializeField] Vector3 displacement;
       
    [SerializeField] float speed;
    [SerializeField] GameObject llanta;
    [SerializeField] float angle;
    AXIS rotationAxis;

    [SerializeField] Vector3[] llantasPos;

    
    Mesh mesh;//mesh del auto
    Mesh[] llantaMeshes = new Mesh[4];
    Vector3[][] llantasVertices = new Vector3[4][];
    Vector3[][] llantasNewVertices = new Vector3[4][];
    Vector3[] baseVertices;
    Vector3[] newVectices;

    float t ;

    void Start()
    {
        mesh = GetComponentInChildren<MeshFilter>().mesh;
        baseVertices = mesh.vertices;
        newVectices = new Vector3[baseVertices.Length];
        for (int i = 0; i < baseVertices.Length; i++)
        {
            newVectices[i] = baseVertices[i];
        }
        generateLlantas();
    }

    void Update()
    {
      
        DoTransform();
    }

    float GetAngle(Vector3 displacement)
    {
        float a = Mathf.Atan2(displacement.x, displacement.z) ; //debe ser asi el auto como las llantas apunta en z siendo el angulo 0
        return a * Mathf.Rad2Deg;
    }

    void DoTransform()
    {
    

        Matrix4x4 move = HW_Transforms.TranslationMat(displacement.x * Time.time,
                                                      displacement.y * Time.time,
                                                      displacement.z * Time.time);

        Matrix4x4 rotate = HW_Transforms.RotateMat(angle, rotationAxis);//rotacion del auto dado al desplazamiento ingresado

        Matrix4x4 composite = move * rotate;//matriz de transformacion del auto, primero rota y luego se mueve 

        Matrix4x4 rotateLlantas = HW_Transforms.RotateMat(Time.time * speed, AXIS.X);//rotacion de las llantas sobre el eje x

        for (int i = 0; i < newVectices.Length; i++)
        {
            Vector4 temp = new Vector4(baseVertices[i].x, baseVertices[i].y, baseVertices[i].z, 1);
             newVectices[i] = composite * temp;//se aplica la matriz de transformacion del auto a los nuevos vertices del auto
        }

        mesh.vertices = newVectices;//se actualizan los vertices del auto con los nuevos
        mesh.RecalculateNormals();//se recalculan las normales del auto

        for (int i = 0; i < llantaMeshes.Length; i++)
        {
            Matrix4x4 posicionLlantas = HW_Transforms.TranslationMat(llantasPos[i].x, llantasPos[i].y, llantasPos[i].z);//posicion de las llantas al inicio
            Matrix4x4 compositeLlantas = composite * posicionLlantas * rotateLlantas;// matriz de transformacion de las llantas, primero se rota sobre su eje, luego se colocan en la posicion repetivo del auto 
                                                                                     //luego se aplica la matriz de transformacion del auto

            for (int j = 0; j < llantasNewVertices[i].Length; j++)
            {
                Vector4 temp = new Vector4(llantasVertices[i][j].x, llantasVertices[i][j].y, llantasVertices[i][j].z, 1);
                llantasNewVertices[i][j] = compositeLlantas * temp;//se aplica la matriz de transformacion de las llantas a los nuevos vertices de las llantas
            }

            llantaMeshes[i].vertices = llantasNewVertices[i];//se actualizan los vertices de las llantas con los nuevos
            llantaMeshes[i].RecalculateNormals();//se saca las normales de las llantas
        }
        
    }

    void generateLlantas()
    {
        Vector3 posicion_original = new Vector3(0, 0, 0);//posicion de las llantas al inicio
        for (int i = 0; i < llantasPos.Length; i++)
        {
            GameObject llantaTemp = Instantiate(llanta, posicion_original, Quaternion.identity);//se instancia la llanta
            llantaMeshes[i] = llantaTemp.GetComponentInChildren<MeshFilter>().mesh;//se obtiene el mesh de la llanta
            llantasVertices[i] = llantaMeshes[i].vertices;//se obtienen los vertices de la llanta
            llantasNewVertices[i] = new Vector3[llantasVertices[i].Length];
            for (int j = 0; j < llantasVertices[i].Length; j++)
            {
                llantasNewVertices[i][j] = llantasVertices[i][j];
            }
        }
    }

    public void setNewPos(Vector3 newPos){
        startPos = stopPos;
        stopPos = newPos;

    }

    Vector3 PositionLerp(Vector3 star, Vector3 stop, float t){
        return star + (stop - star) * t;
    }

    float GetT(){
        return t*t;
    }
}


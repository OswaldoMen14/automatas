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
    [SerializeField] float ti = 0f;
    public float moveTime = 0f;
    [SerializeField] float elapsedTime = 0f;
    
    [Header("Transform of wheels")]
    [SerializeField] float speedRotation;
    [SerializeField] GameObject llanta;
    [SerializeField] float angle;
    [SerializeField] Vector3[] llantasPos;

    Dictionary<string, GameObject> llantas = new Dictionary<string, GameObject>();

    



    
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
        ti = elapsedTime / moveTime;

        Vector3 displacement = startPos + (stopPos - startPos) * ti;//desplazamiento del auto
        elapsedTime += Time.deltaTime;

        Matrix4x4 move = HW_Transforms.TranslationMat(displacement.x ,
                                                      displacement.y ,
                                                      displacement.z );

        

        Matrix4x4 rotate = HW_Transforms.RotateMat(angle, AXIS.Y);//rotacion del auto dado al desplazamiento ingresado

        Matrix4x4 composite = move * rotate;//matriz de transformacion del auto, primero rota y luego se mueve 

        Matrix4x4 rotateLlantas = HW_Transforms.RotateMat(Time.time * speedRotation, AXIS.X);//rotacion de las llantas sobre el eje x

        for (int i = 0; i < newVectices.Length; i++)
        {
            Vector4 temp = new Vector4(baseVertices[i].x, baseVertices[i].y, baseVertices[i].z, 1);
             newVectices[i] = composite * temp;//se aplica la matriz de transformacion del auto a los nuevos vertices del auto
        }

        mesh.vertices = newVectices;//se actualizan los vertices del auto con los nuevos
        mesh.RecalculateNormals();//se recalculan las normales del auto
        mesh.RecalculateBounds();



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
            llantaMeshes[i].RecalculateBounds();
        }
        
    }

    public void DestroyLlantas (){
        for (int i = 0; i < llantasPos.Length; i++)
        {
            Destroy(llantas[i.ToString()]);
        }
    }

    void generateLlantas()
    {
        Vector3 posicion_original = new Vector3(0, 0, 0);//posicion de las llantas al inicio
        for (int i = 0; i < llantasPos.Length; i++)
        {
            //de int a string

            llantas[i.ToString()] = Instantiate(llanta, posicion_original, Quaternion.identity);//se instancia la llanta
            llantaMeshes[i] = llantas[i.ToString()].GetComponentInChildren<MeshFilter>().mesh;//se obtiene el mesh de la llanta
            llantasVertices[i] = llantaMeshes[i].vertices;//se obtienen los vertices de la llanta
            llantasNewVertices[i] = new Vector3[llantasVertices[i].Length];
            for (int j = 0; j < llantasVertices[i].Length; j++)
            {
                llantasNewVertices[i][j] = llantasVertices[i][j];
            }
        }
    }

    public void SetNewPos(Vector3 newPos){
        startPos = stopPos;
        stopPos = newPos;
        if(startPos != stopPos){
            angle = GetAngle(stopPos-startPos);  
        }
        elapsedTime = 0f;

    }

}


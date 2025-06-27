import asyncio
import json
from typing import Dict, Any, List
from nutrisense_agents.api.services.react_agent_service import stream_nutrisense_react_agent

async def test_stream_nutrisense_react_agent():
    """
    Test para probar el streaming del react agent de NutriSense
    """
    print("🧪 Iniciando test de streaming del React Agent de NutriSense...")
    print("=" * 80)
    
    # Usuario de prueba
    test_user_uid = "db34fd60-d91f-4845-b8ac-b95c6fd60322"
    
    # Mensajes de prueba
    test_cases = [
        {
            "name": "Consulta nutricional básica",
            "messages": [
                {"role": "user", "content": "¿Puedes ayudarme a registrar mi desayuno?"}
            ]
        },
        {
            "name": "Agregar ingrediente",
            "messages": [
                {"role": "user", "content": "Quiero agregar avena como ingrediente a mi base de datos"}
            ]
        },
        {
            "name": "Consultar plan de comidas",
            "messages": [
                {"role": "user", "content": "¿Cuál es mi plan de comidas para hoy?"}
            ]
        },
        {
            "name": "Pregunta general",
            "messages": [
                {"role": "user", "content": "¿Qué alimentos son ricos en proteína?"}
            ]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test Case {i}: {test_case['name']}")
        print("-" * 50)
        print(f"👤 Usuario: {test_user_uid}")
        print(f"💬 Mensaje: {test_case['messages'][0]['content']}")
        print("\n📡 Streaming response:")
        print("-" * 30)
        
        try:
            chunk_count = 0
            total_content = ""
            
            # Ejecutar el streaming
            async for chunk in stream_nutrisense_react_agent(
                user_uid=test_user_uid,
                messages=test_case['messages']
            ):
                chunk_count += 1
                
                # Mostrar información del chunk
                print(f"📦 Chunk {chunk_count}:")
                
                # Si el chunk tiene mensajes, mostrar el contenido
                if isinstance(chunk, dict):
                    # Formatear el chunk para mejor visualización
                    if 'messages' in chunk:
                        for msg in chunk['messages']:
                            if hasattr(msg, 'content') and msg.content:
                                print(f"   📝 Contenido: {msg.content[:100]}{'...' if len(str(msg.content)) > 100 else ''}")
                                total_content += str(msg.content)
                            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                print(f"   🛠️  Tool calls: {len(msg.tool_calls)}")
                                for tool_call in msg.tool_calls:
                                    print(f"      - {tool_call.get('name', 'unknown')} con args: {str(tool_call.get('args', {}))[:50]}...")
                    
                    # Si hay otros datos interesantes, mostrarlos
                    if 'agent' in chunk:
                        print(f"   🤖 Agent step: {chunk.get('agent', {}).get('type', 'unknown')}")
                    
                    if 'tools' in chunk:
                        print(f"   🔧 Tools step: {len(chunk.get('tools', []))} tool results")
                
                print()
                
                # Limitar el número de chunks para evitar spam
                if chunk_count >= 20:
                    print("   ⚠️  Limitando output a 20 chunks...")
                    break
            
            print(f"✅ Test completado - Total chunks: {chunk_count}")
            print(f"📊 Contenido total generado: {len(total_content)} caracteres")
            
        except Exception as e:
            print(f"❌ Error en test case {i}: {str(e)}")
            print(f"   Tipo de error: {type(e).__name__}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 80)
        
        # Pausa entre tests para mejor legibilidad
        if i < len(test_cases):
            print("⏳ Esperando 2 segundos antes del siguiente test...")
            await asyncio.sleep(2)

async def test_simple_stream():
    """
    Test simple y rápido para verificar que el streaming funciona
    """
    print("\n🚀 Test simple de streaming...")
    
    user_uid = "simple_test_user"
    messages = [{"role": "user", "content": "Hola, ¿puedes ayudarme?"}]
    
    try:
        chunk_count = 0
        async for chunk in stream_nutrisense_react_agent(user_uid, messages):
            chunk_count += 1
            print(f"✨ Chunk {chunk_count} recibido")
            
            # Solo mostrar los primeros 3 chunks
            if chunk_count >= 3:
                print("⚡ Test simple completado exitosamente!")
                break
        
        return True
    except Exception as e:
        print(f"❌ Error en test simple: {str(e)}")
        return False

async def main():
    """
    Función principal para ejecutar todos los tests
    """
    print("🎯 TESTS DE STREAMING REACT AGENT NUTRISENSE")
    print("=" * 80)
    
    # Ejecutar test simple primero
    simple_success = await test_simple_stream()
    
    if simple_success:
        print("\n🎉 Test simple exitoso! Procediendo con tests completos...\n")
        await test_stream_nutrisense_react_agent()
    else:
        print("\n⚠️  Test simple falló. Revisa la configuración antes de continuar.")
    
    print("\n🏁 Todos los tests completados!")

if __name__ == "__main__":
    # Ejecutar el test
    asyncio.run(main()) 
import asyncio
from nutrisense_agents.api.services.react_agent_service import stream_nutrisense_react_agent

def print_separator(title="", char="-"):
    """Imprime un separador con título opcional"""
    if title:
        print(f"\n{char * 20} {title} {char * 20}")
    else:
        print(char * 60)

def format_content(content, max_length=None):
    """Formatea el contenido para mostrarlo de manera legible"""
    if not content:
        return ""
    
    content_str = str(content)
    if max_length and len(content_str) > max_length:
        return content_str[:max_length] + f"...\n[Contenido truncado - {len(content_str)} caracteres total]"
    return content_str

def format_tool_error(content, max_length=2000):
    """Formatea errores de herramientas para mostrarlos completos"""
    if not content:
        return ""
    
    content_str = str(content)
    
    # Si es un error de herramienta, mostrar más información
    if "Error:" in content_str or "ToolException" in content_str:
        if max_length and len(content_str) > max_length:
            return content_str[:max_length] + f"...\n[Error truncado - {len(content_str)} caracteres total]"
        return content_str
    
    # Para otros contenidos, usar límite normal
    if max_length and len(content_str) > max_length:
        return content_str[:max_length] + "..."
    return content_str

async def test_stream_basic():
    """Test básico de streaming con output completo"""
    print("🚀 Test básico de streaming...")
    
    user_uid = "db34fd60-d91f-4845-b8ac-b95c6fd60322"
    messages = [{"role": "user", "content": "lo que estoy comiendo es sano?"}]
    
    print(f"👤 Usuario: {user_uid}")
    print(f"💬 Mensaje: {messages[0]['content']}")
    
    print_separator("STREAMING OUTPUT")
    
    chunk_count = 0
    total_content = ""
    
    try:
        async for chunk in stream_nutrisense_react_agent(user_uid, messages):
            chunk_count += 1
            print(f"\n🔄 CHUNK {chunk_count} - Tipo: {type(chunk).__name__}")
            
            if isinstance(chunk, dict):
                # Mostrar todas las keys principales
                print(f"   🔑 Keys disponibles: {list(chunk.keys())}")
                
                # Procesar mensajes
                if 'messages' in chunk:
                    print(f"   📨 Mensajes encontrados: {len(chunk['messages'])}")
                    
                    for i, msg in enumerate(chunk['messages']):
                        print(f"\n   📝 MENSAJE {i + 1}:")
                        
                        # Mostrar rol si existe
                        if hasattr(msg, 'role'):
                            print(f"      👤 Rol: {msg.role}")
                        
                        # Mostrar contenido completo
                        if hasattr(msg, 'content') and msg.content:
                            # Para errores de herramientas, mostrar más contenido
                            if hasattr(msg, 'role') and msg.role == 'tool':
                                content = format_tool_error(msg.content, None)  # Sin límite
                                print(f"      🔧 Error de herramienta:")
                                print(f"         {content}")
                            else:
                                content = format_content(msg.content, None)  # Sin límite
                                print(f"      💬 Contenido:")
                                print(f"         {content}")
                            
                            # Acumular contenido del assistant
                            if hasattr(msg, 'role') and msg.role == 'assistant':
                                total_content += str(msg.content) + "\n"
                        
                        # Mostrar tool calls si existen
                        if hasattr(msg, 'tool_calls') and msg.tool_calls:
                            print(f"      🔧 Tool Calls ({len(msg.tool_calls)}):")
                            for j, tool_call in enumerate(msg.tool_calls):
                                tool_name = tool_call.get('name', 'unknown')
                                tool_args = tool_call.get('args', {})
                                print(f"         {j + 1}. {tool_name}")
                                print(f"            Args: {format_content(tool_args, None)}")  # Sin límite
                        
                        # Mostrar información adicional de mensajes de herramientas
                        if hasattr(msg, 'role') and msg.role == 'tool':
                            if hasattr(msg, 'name'):
                                print(f"      🔧 Nombre de herramienta: {msg.name}")
                            if hasattr(msg, 'tool_call_id'):
                                print(f"      🆔 Tool call ID: {msg.tool_call_id}")
                
                # Mostrar otros datos relevantes
                for key in chunk.keys():
                    if key not in ['messages']:
                        value = chunk[key]
                        if isinstance(value, (list, dict)):
                            print(f"   📊 {key}: {type(value).__name__} con {len(value) if hasattr(value, '__len__') else 'N/A'} elementos")
                        else:
                            print(f"   📊 {key}: {format_content(value, None)}")  # Sin límite
            
            else:
                print(f"   📦 Contenido directo: {format_content(chunk, None)}")  # Sin límite
            
            print("   " + "─" * 50)
            
            # No limitar tanto para ver todo el output
            if chunk_count >= 20:
                print("⚠️ Limitando a 20 chunks para evitar spam...")
                break
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print_separator("RESUMEN FINAL")
    print(f"✅ Test completado - {chunk_count} chunks procesados")
    
    if total_content.strip():
        print("\n📄 CONTENIDO COMPLETO DEL ASSISTANT:")
        print("=" * 60)
        print(total_content.strip())
        print("=" * 60)

async def test_stream_with_tool_usage():
    """Test de streaming con uso de tools y output detallado"""
    print("\n🛠️ Test de streaming con posible uso de tools...")
    
    user_uid = "db34fd60-d91f-4845-b8ac-b95c6fd60322"
    messages = [{"role": "user", "content": "crea un plan nutricional para mi semana actual"}]
    
    print(f"👤 Usuario: {user_uid}")
    print(f"💬 Mensaje: {messages[0]['content']}")
    
    print_separator("STREAMING OUTPUT CON TOOLS")
    
    chunk_count = 0
    tool_calls_detected = 0
    assistant_responses = []
    tool_errors = []
    
    try:
        async for chunk in stream_nutrisense_react_agent(user_uid, messages):
            chunk_count += 1
            print(f"\n🔄 CHUNK {chunk_count}")
            
            if isinstance(chunk, dict):
                # Análisis detallado de mensajes
                if 'messages' in chunk:
                    for i, msg in enumerate(chunk['messages']):
                        print(f"\n   📝 MENSAJE {i + 1}:")
                        
                        if hasattr(msg, 'role'):
                            print(f"      👤 Rol: {msg.role}")
                        
                        # Contenido del mensaje
                        if hasattr(msg, 'content') and msg.content:
                            # Manejo especial para errores de herramientas
                            if hasattr(msg, 'role') and msg.role == 'tool':
                                content = format_tool_error(msg.content, None)  # Sin límite
                                print(f"      🚨 ERROR DE HERRAMIENTA:")
                                print(f"         {content}")
                                tool_errors.append({
                                    'tool_name': getattr(msg, 'name', 'unknown'),
                                    'error': str(msg.content)
                                })
                            else:
                                content = format_content(msg.content, None)  # Sin límite
                                print(f"      💬 Contenido completo:")
                                print(f"         {content}")
                            
                            if hasattr(msg, 'role') and msg.role == 'assistant':
                                assistant_responses.append(str(msg.content))
                        
                        # Tool calls detallados
                        if hasattr(msg, 'tool_calls') and msg.tool_calls:
                            tool_calls_detected += len(msg.tool_calls)
                            print(f"      🔧 TOOL CALLS ({len(msg.tool_calls)}):")
                            
                            for j, tool_call in enumerate(msg.tool_calls):
                                tool_name = tool_call.get('name', 'unknown')
                                tool_args = tool_call.get('args', {})
                                tool_id = tool_call.get('id', 'no-id')
                                
                                print(f"         🔧 Tool {j + 1}: {tool_name}")
                                print(f"            ID: {tool_id}")
                                print(f"            Argumentos:")
                                
                                # Mostrar argumentos de manera estructurada
                                if isinstance(tool_args, dict):
                                    for arg_key, arg_value in tool_args.items():
                                        print(f"              {arg_key}: {format_content(arg_value, None)}")  # Sin límite
                                else:
                                    print(f"              {format_content(tool_args, None)}")  # Sin límite
                        
                        # Información adicional para mensajes de herramientas
                        if hasattr(msg, 'role') and msg.role == 'tool':
                            if hasattr(msg, 'name'):
                                print(f"      🔧 Herramienta: {msg.name}")
                            if hasattr(msg, 'tool_call_id'):
                                print(f"      🆔 Call ID: {msg.tool_call_id}")
                
                # Mostrar información adicional del chunk
                other_keys = [k for k in chunk.keys() if k != 'messages']
                if other_keys:
                    print(f"\n   📊 DATOS ADICIONALES:")
                    for key in other_keys:
                        value = chunk[key]
                        print(f"      {key}: {format_content(value, None)}")  # Sin límite
            
            print("   " + "─" * 50)
            
            if chunk_count >= 25:
                print("⚠️ Limitando a 25 chunks...")
                break
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print_separator("RESUMEN FINAL CON TOOLS")
    print(f"✅ Test completado - {chunk_count} chunks, {tool_calls_detected} tool calls detectadas")
    
    if tool_errors:
        print(f"\n🚨 ERRORES DE HERRAMIENTAS ({len(tool_errors)}):")
        print("=" * 60)
        for i, error in enumerate(tool_errors):
            print(f"\nError {i + 1} - Herramienta: {error['tool_name']}")
            print(f"Mensaje: {error['error']}")
            print("-" * 40)
        print("=" * 60)
    
    if assistant_responses:
        print(f"\n📄 RESPUESTAS DEL ASSISTANT ({len(assistant_responses)}):")
        print("=" * 60)
        for i, response in enumerate(assistant_responses):
            print(f"\nRespuesta {i + 1}:")
            print(response)
            print("-" * 40)
        print("=" * 60)

async def main():
    """Ejecutar todos los tests"""
    print("🧪 TESTS DE STREAMING NUTRISENSE REACT AGENT")
    print("=" * 80)
    
    await test_stream_basic()
    
    print("\n" + "=" * 80)
    
    await test_stream_with_tool_usage()
    
    print(f"\n🏁 Tests completados!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main()) 
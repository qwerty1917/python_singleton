""""""
"""
어떤 클래스의 경우 단 하나의 객체만 생성되어야 한다.
예를들어 시스템에 많은 프린터가 있더라도 프린터 스풀은 한곳이어야 하고 파일 시스템 윈도우 관리자 등도 하나여야 함.

싱글톤 구현 특징
1. 클래스에서 추가적인 인스턴스가 생성되지 못하도록 차단
2. 클래스 자체에서 인스턴스에 접근하는 방법을 제공
3. 유일한 인스턴스가 서브클래싱으로 확장되어 여러 클래스의 선택지를 제공

싱글톤의 장점
1. 클래스 자체에서 인스턴스를 캡슐화하기 때문에 사용자가 언제 어떻게 인스턴스에 접근할지 통제할 수 있다. 이편이 유일한 인스턴스의 보장이라는 싱글톤 패턴의 의의
    에도 부합함
2. 전역 변수를 사용함으로써 네임스페이스를 깔끔하게 관리할 수 있게 도와줌
3. 한 클래스에서는 하나의 인스턴스만이 생성될 수 있지만, 다른 버전의 인스턴스가 필요하면 기존 클래스를 상속하여 그 자손 클래스의 단독 인스턴스를 만드는 식으로
    해결 가능
"""


# 1. 인스턴스의 유일성 보장


class Singleton:
    # 책에 나온 c++ 코드에서는 생성자를 protected 로 선언하여 생성자에 직접 접근하는것을 막지만 파이썬에선 __init__ 메서드를 오버라이딩함.

    @staticmethod
    def instance(**kwargs):
        # 클래스 변수에서 __unique_instance__ 를 불러와봄
        instance = Singleton.__dict__.get("__unique_instance__")

        # __unique_instance__ 에 이미 생성된 인스턴스가 있다면 그 인스턴스를 반환
        if instance is not None:
            return instance

        # 아직 생성된 인스턴스가 없다면 인스턴스를 생성해 주고 클래스 변수 __unique_instance__ 에 지정해 준다.
        else:
            Singleton.__unique_instance__ = Singleton(allowed_access=True, **kwargs)

            return Singleton.__unique_instance__

    # allowed_access 인자의 기본값을 False 로 하여 instance 메소드를 통하지 않고 직접 생성 시도시 에러 반환
    def __init__(self, allowed_access=False, **kwargs):
        if not allowed_access:
            raise Exception("[Error]: creating an instance directly is not available.\n")
        self.__instance_name__ = kwargs["name"]

    def get_name(self):
        return self.__instance_name__

    @staticmethod
    # Singleton 클래스에 등록된 인스턴스를 삭제하는 static 메소드.
    def del_instance():
        Singleton.__unique_instance__ = None


# 인스턴스 확인용
def print_instance_info(instance):
    print("  instance id: " + str(id(instance)))
    print("  instance name: " + instance.get_name())
    print("  class name: " + type(instance).__name__)
    print("")


print("creating first instance.")
print_instance_info(Singleton.instance(name="first created Singleton"))

print("trying to create second instance.")
print_instance_info(Singleton.instance(name="second created Singleton"))

print("trying c = Singleton()")
try:
    print_instance_info(Singleton(name="third created Singleton"))
except Exception as e:
    print(e)

"""
creating first instance.
  instance id: 4323552952
  instance name: first created Singleton
  class name: Singleton

trying to create second instance.
  instance id: 4323552952
  instance name: first created Singleton
  class name: Singleton

trying c = Singleton()
[Error]: creating an instance directly is not available.
"""


# 2. Singleton 클래스를 서브클래싱

# 여러가지 서브 클래스들이 있을 때 그중 어느 것을 사용하냐에 따라서 Singleton 클래스의 instance() 에서 어느 클래스의 인스턴스를 생설할지 구분해 주어야 한다
# 관리의 편의성을 위해, 타입 지정 문자열과 실제 클래스를 매칭하는 함수 __look_up__을 스태틱 메소드로 정의해 둔다
# 서브 클래스가 여러개 있으며 서브 클래스로부터 생성된 인스턴스라도 최상위 클래스인 SingletonWithSubs 의 __unique_instance__ 변수에 등록되므로
# 서브 클래스가 여럿 있더라도 실제 인스턴스는 하나이다. 여기서 서브 클래스의 의미는 사용 가능한 버전중 어느 것을 사용할 것인지에 대한 선택과 같다.


class SingletonWithSubs:

    #현재 어느 클래스에서 실행된 함수인지 판단하기위해 @staticmethod 대신 @classmethod 사용
    @classmethod
    def instance(cls, **kwargs):
        instance = SingletonWithSubs.__dict__.get("__unique_instance__")

        if instance is not None:
            return instance

        else:
            # 부모 클래스를 통해 인스턴스를 생성하지 않고 서브클래스로 직접 생성하게되면 인스턴스의 유일성이 깨지게 된다.
            # 따라서 부모 클래스를 통한 인스턴스 생성이 아니라면 오류가 발생하도록 한다.
            if cls.__name__ != "SingletonWithSubs":
                raise Exception("[Error]: creating an instance from a subclass is not available.\n")

            # 선택된 서브 클래스를 이용하여 인스턴스를 생성한다.
            sub_cls = SingletonWithSubs.__look_up__(kwargs["type"])

            # 서브 클래스로 인스턴스를 생성한 후엔 부모 클래스인 SingletonWithSubs에 생성된 인스턴스를 등록시킨다.
            cls.__unique_instance__ = sub_cls(allowed_access=True, **kwargs)
            return cls.__unique_instance__

    def __init__(self, allowed_access=False, **kwargs):
        if not allowed_access:
            raise Exception("[Error]: creating an instance directly is not available.\n")
        self.__instance_name__ = kwargs["name"]

    @staticmethod
    # 선택된 서브클래스를 반환. 이 함수는 새 서브클래스가 늘어날 때마다 수정되어야 한다.
    def __look_up__(env_name):
        switcher = {
            "type0": SingletonType0,
            "type1": SingletonType1,
            "type2": SingletonType2,
            "type3": SingletonType3
        }

        return switcher[env_name]

    @staticmethod
    def del_instance():
        SingletonWithSubs.__unique_instance__ = None

    def get_name(self):
        return self.__instance_name__


# 서브클래스들 정의
class SingletonType0(SingletonWithSubs):
    pass


class SingletonType1(SingletonWithSubs):
    pass


class SingletonType2(SingletonWithSubs):
    pass


# 오버라이딩이 있는 서브 클래스
class SingletonType3(SingletonWithSubs):
    def get_name(self):
        return "This instance is \"" + self.__instance_name__ + "\" of SingletonType3."


print("\n====================\n")
# 서브클래스를 사용하더라도 a = SingletonType3.instance(name="my_instance") 이런식이 아니라
# 부모 클래스인 SingletonWithSubs.instance(**kwargs) 를 이용하여 생성해 준다.
# 이때 인자로 어느 서브클래스를 사용할 것인지 인자를 넘긴다.
print("creating first instance of type0.")
# t0_1 = SingletonWithSubs.instance(type="type0", name="t0_1")
print_instance_info(SingletonWithSubs.instance(type="type0", name="t0_1"))

print("trying to create second instance of type0.")
# t0_2 = SingletonWithSubs.instance(type="type0", name="t0_2")
print_instance_info(SingletonWithSubs.instance(type="type0", name="t0_2"))

print("trying to create first instance of type1 without deleting instance.")
# t1_1 = SingletonWithSubs.instance(type="type1", name="t1_1")
print_instance_info(SingletonWithSubs.instance(type="type1", name="t1_1"))

print("creating first instance of type2 after deleting instance.")
SingletonWithSubs.del_instance()
# t2_1 = SingletonWithSubs.instance(type="type2", name="t2_1")
print_instance_info(SingletonWithSubs.instance(type="type2", name="t2_1"))

print("creating first instance of type3 with method overriding.")
SingletonWithSubs.del_instance()
# t3_1 = SingletonWithSubs.instance(type="type3", name="t3_1")
print_instance_info(SingletonWithSubs.instance(type="type3", name="t3_1"))

print("trying t3_2 = SingletonType3.instance(name = \"t3_2\")")
SingletonWithSubs.del_instance()
try:
    # t3_2 = SingletonType3.instance(name="t3_2")
    print_instance_info(SingletonType3.instance(name="t3_2"))
except Exception as e:
    print(e)

print("trying t3_3 = SingletonType3(name = \"t3_3\")")
SingletonWithSubs.del_instance()
try:
    # t3_3 = SingletonType3(name="t3_3")
    print_instance_info(SingletonType3(name="t3_3"))
except Exception as e:
    print(e)

"""
creating first instance of type0.
  instance id: 4323578096
  instance name: t0_1
  class name: SingletonType0

trying to create second instance of type0.
  instance id: 4323578096
  instance name: t0_1
  class name: SingletonType0

trying to create first instance of type1 without deleting instance.
  instance id: 4323578096
  instance name: t0_1
  class name: SingletonType0

creating first instance of type2 after deleting instance.
  instance id: 4323578208
  instance name: t2_1
  class name: SingletonType2

creating first instance of type3 with method overriding.
  instance id: 4323578264
  instance name: This instance is "t3_1" of SingletonType3.
  class name: SingletonType3

trying t3_2 = SingletonType3.instance(name = "t3_2")
[Error]: creating an instance from a subclass is not available.

trying t3_3 = SingletonType3(name = "t3_3")
[Error]: creating an instance directly is not available.
"""
